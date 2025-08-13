import asyncio
import json
from datetime import datetime, UTC
from flask import Flask, request, jsonify

from microservice_math.app.db import init_db

app = Flask(__name__)
app.secret_key = "mathsecretkey"


def get_username_from_request():
    return request.headers.get("X-Username", "anonymous")


@app.route("/pow")
def compute_pow():
    base = request.args.get("base", type=float)
    exp = request.args.get("exp", type=float)
    result = base**exp if base is not None and exp is not None else None

    if base is not None and exp is not None:
        username = get_username_from_request()
        asyncio.run(log_to_db("pow", {"base": base, "exp": exp}, result, username))

    return jsonify(
        {"operation": "pow", "base": base, "exp": exp, "result": result}
    )


@app.route("/factorial")
def compute_factorial():
    n = request.args.get("n", type=int)
    result = None
    if n is not None and n >= 0:
        result = 1
        for i in range(2, n + 1):
            result *= i

        username = get_username_from_request()
        asyncio.run(log_to_db("factorial", {"n": n}, result, username))

    return jsonify({"operation": "factorial", "n": n, "result": result})


@app.route("/fibonacci")
def compute_fibonacci():
    n = request.args.get("n", type=int)
    result = None
    if n is not None and n >= 0:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        result = a

        username = get_username_from_request()
        asyncio.run(log_to_db("fibonacci", {"n": n}, result, username))

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
