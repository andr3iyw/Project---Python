
import asyncio
import json
import requests
from flask import Blueprint, request, jsonify

from app.controllers import math_controller
from app.schemas.math_models import PowInput, FactorialInput, FibonacciInput

math_blueprint = Blueprint("math", __name__)

@math_blueprint.route("/pow")
def compute_pow():
    data = PowInput(base=request.args.get("base"), exponent=request.args.get("exp"))
    result = asyncio.run(math_controller.compute_pow(data.base, data.exponent))

    # Send log to DB microservice
    log_data = {
        "operation": "pow",
        "input_data": json.dumps({"base": data.base, "exp": data.exponent}),
        "result": str(result)
    }
    try:
        requests.post("http://localhost:7000/log", json=log_data, timeout=2)
    except Exception as e:
        print("LOG ERROR:", e)

    return jsonify({"operation": "pow", "base": data.base, "exp": data.exponent, "result": result})

@math_blueprint.route("/factorial")
def compute_factorial():
    data = FactorialInput(n=request.args.get("n"))
    result = asyncio.run(math_controller.compute_factorial(data.n))

    log_data = {
        "operation": "factorial",
        "input_data": json.dumps({"n": data.n}),
        "result": str(result)
    }
    try:
        requests.post("http://localhost:7000/log", json=log_data, timeout=2)
    except Exception as e:
        print("LOG ERROR:", e)

    return jsonify({"operation": "factorial", "n": data.n, "result": result})

@math_blueprint.route("/fibonacci")
def compute_fibonacci():
    data = FibonacciInput(n=request.args.get("n"))
    result = asyncio.run(math_controller.compute_fibonacci(data.n))

    log_data = {
        "operation": "fibonacci",
        "input_data": json.dumps({"n": data.n}),
        "result": str(result)
    }
    try:
        requests.post("http://localhost:7000/log", json=log_data, timeout=2)
    except Exception as e:
        print("LOG ERROR:", e)

    return jsonify({"operation": "fibonacci", "n": data.n, "result": result})

@math_blueprint.route("/logs")
def get_logs():
    try:
        resp = requests.get("http://localhost:7000/logs", timeout=2)
        if resp.status_code == 200:
            return jsonify(resp.json())
        else:
            return jsonify({"error": "Failed to fetch logs from DB microservice."}), 500
    except Exception as e:
        print("LOG FETCH ERROR:", e)
        return jsonify({"error": str(e)}), 500
