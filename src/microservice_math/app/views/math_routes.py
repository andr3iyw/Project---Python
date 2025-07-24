import asyncio
import json
from flask import Blueprint, request, jsonify

from app.controllers import math_controller
from app.schemas.math_models import PowInput, FactorialInput, FibonacciInput
from app.db import get_db_connection
from app.models.request_log import insert_log

math_blueprint = Blueprint("math", __name__)

@math_blueprint.route("/pow")
def compute_pow():
    data = PowInput(base=request.args.get("base"), exponent=request.args.get("exp"))
    result = asyncio.run(math_controller.compute_pow(data.base, data.exponent))

    db =  asyncio.run(get_db_connection())
    input_json = json.dumps({"base": data.base, "exp": data.exponent})
    result_str = str(result)
    asyncio.run(insert_log(db, "pow", input_json, result_str))

    return jsonify({"operation": "pow", "base": data.base, "exp": data.exponent, "result": result})

@math_blueprint.route("/factorial")
def compute_factorial():
    data = FactorialInput(n=request.args.get("n"))
    result = asyncio.run(math_controller.compute_factorial(data.n))

    db = asyncio.run(get_db_connection())
    input_json = json.dumps({"n": data.n})
    result_str = str(result)
    asyncio.run(insert_log(db, "factorial", input_json, result_str))

    return jsonify({"operation": "factorial", "n": data.n, "result": result})

@math_blueprint.route("/fibonacci")
def compute_fibonacci():
    data = FibonacciInput(n=request.args.get("n"))
    result = asyncio.run(math_controller.compute_fibonacci(data.n))

    db = asyncio.run(get_db_connection())
    input_json = json.dumps({"n": data.n})
    result_str = str(result)
    asyncio.run(insert_log(db, "fibonacci", input_json, result_str))

    return jsonify({"operation": "fibonacci", "n": data.n, "result": result})

@math_blueprint.route("/logs")
def get_logs():
    try:
        db = asyncio.run(get_db_connection())

        async def fetch():
            async with db.execute("SELECT * FROM request_log ORDER BY id DESC LIMIT 20;") as cursor:
                rows = await cursor.fetchall()
            await db.close()
            return rows

        rows = asyncio.run(fetch())

        logs = [
            {"id": row[0], "operation": row[1], "input_data": row[2], "result": row[3], "timestamp": row[4]}
            for row in rows
        ]
        return jsonify(logs)

    except Exception as e:
        print("LOG FETCH ERROR:", e)
        return jsonify({"error": str(e)}), 500
