# Read limits from config file
import os
def read_limits_config(path):
    limits = {}
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, val = line.split('=')
                    limits[key.strip()] = int(val.strip())
    return limits

LIMITS = read_limits_config(os.path.join(os.path.dirname(__file__), 'limits.cfg'))

import asyncio
import json
from datetime import datetime, UTC
from flask import Flask, request, jsonify
import redis
from microservice_math.app.db import init_db

app = Flask(__name__)
app.secret_key = "mathsecretkey"


# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Caching flag: 0 = disabled, 1 = enabled
CACHE_ENABLED = 0


def get_username_from_request():
    return request.headers.get("X-Username", "anonymous")


@app.route("/pow")
def compute_pow():
    base = request.args.get("base", type=float)
    exp = request.args.get("exp", type=float)
    result = None
    max_base = LIMITS.get('POW_MAX_BASE', 1e6)
    max_exp = LIMITS.get('POW_MAX_EXP', 1000)
    if base is not None and abs(base) > max_base:
        return jsonify({"error": f"Base exceeds max allowed value ({max_base})"}), 400
    if exp is not None and abs(exp) > max_exp:
        return jsonify({"error": f"Exponent exceeds max allowed value ({max_exp})"}), 400
    op_str = f"pow:{base}:{exp}"
    cached = redis_client.get(op_str) if CACHE_ENABLED else None
    try:
        if CACHE_ENABLED:
            if cached is not None:
                result = float(cached)
            elif base is not None and exp is not None:
                result = base ** exp
                asyncio.run(log_to_db("pow", {"base": base, "exp": exp}, result, get_username_from_request()))
                redis_client.set(op_str, result)
            else:
                result = None
            if cached is None and base is not None and exp is not None:
                import time
                time.sleep(5)
        else:
            result = base ** exp if base is not None and exp is not None else None
            if base is not None and exp is not None:
                asyncio.run(log_to_db("pow", {"base": base, "exp": exp}, result, get_username_from_request()))
    except (OverflowError, ValueError) as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 400
    return jsonify({"operation": "pow", "base": base, "exp": exp, "result": result})


@app.route("/factorial")
def compute_factorial():
    n = request.args.get("n", type=int)
    result = None
    max_n = LIMITS.get('FACTORIAL_MAX_N', 10000)
    if n is not None and n > max_n:
        return jsonify({"error": f"n exceeds max allowed value ({max_n})"}), 400
    op_str = f"factorial:{n}"
    cached = redis_client.get(op_str) if CACHE_ENABLED else None
    try:
        if CACHE_ENABLED:
            if cached is not None:
                result = int(cached)
            elif n is not None and n >= 0:
                result = 1
                for i in range(2, n + 1):
                    result *= i
                asyncio.run(log_to_db("factorial", {"n": n}, result, get_username_from_request()))
                redis_client.set(op_str, result)
            if cached is None and n is not None and n >= 0:
                import time
                time.sleep(5)
        else:
            if n is not None and n >= 0:
                result = 1
                for i in range(2, n + 1):
                    result *= i
                asyncio.run(log_to_db("factorial", {"n": n}, result, get_username_from_request()))
    except (OverflowError, ValueError) as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 400
    return jsonify({"operation": "factorial", "n": n, "result": result})


@app.route("/fibonacci")
def compute_fibonacci():
    n = request.args.get("n", type=int)
    result = None
    max_n = LIMITS.get('FIBONACCI_MAX_N', 100000)
    if n is not None and n > max_n:
        return jsonify({"error": f"n exceeds max allowed value ({max_n})"}), 400
    op_str = f"fibonacci:{n}"
    cached = redis_client.get(op_str) if CACHE_ENABLED else None
    try:
        if CACHE_ENABLED:
            if cached is not None:
                result = int(cached)
            elif n is not None and n >= 0:
                a, b = 0, 1
                for _ in range(n):
                    a, b = b, a + b
                result = a
                asyncio.run(log_to_db("fibonacci", {"n": n}, result, get_username_from_request()))
                redis_client.set(op_str, result)
            if cached is None and n is not None and n >= 0:
                import time
                time.sleep(5)
        else:
            if n is not None and n >= 0:
                a, b = 0, 1
                for _ in range(n):
                    a, b = b, a + b
                result = a
                asyncio.run(log_to_db("fibonacci", {"n": n}, result, get_username_from_request()))
    except (OverflowError, ValueError) as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 400
    return jsonify({"operation": "fibonacci", "n": n, "result": result})


@app.route("/logs")
def get_logs():
    try:
        username = get_username_from_request()
        rows = asyncio.run(fetch_logs_from_db(username))
        logs = [
            {
                "id": row[0],
                "operation": row[1],
                "input_data": row[2],
                "result": row[3],
                "timestamp": row[4],
                "user ": row[5]
            }
            for row in rows
        ]
        return jsonify(logs)
    except Exception as e:
        print("LOG FETCH ERROR:", e)
        return jsonify({"error": str(e)}), 500


# helpers


async def log_to_db(operation: str, input_data: dict, result, username: str):
    from microservice_math.app.db import get_db_connection
    from auth_service.models.request_log import insert_log

    db = await get_db_connection()
    input_json = json.dumps(input_data)
    await insert_log(db, operation, input_json, str(result), username)
    await db.close()


async def fetch_logs_from_db(username):
    from microservice_math.app.db import get_db_connection

    db = await get_db_connection()
    async with db.execute(
        "SELECT * FROM request_log WHERE username = ? ORDER BY id DESC LIMIT 20;", (username,)
    ) as cursor:
        rows = await cursor.fetchall()
    await db.close()
    return rows


if __name__ == "__main__":
    asyncio.run(init_db())
    app.run(host="0.0.0.0", port=5002, debug=True)
