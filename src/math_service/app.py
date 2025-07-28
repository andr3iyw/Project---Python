from flask import Flask, request, jsonify

def create_app():
    app = Flask(__name__)
    app.secret_key = "mathsecretkey"

    @app.route("/pow")
    def compute_pow():
        base = request.args.get("base", type=float)
        exp = request.args.get("exp", type=float)
        result = base ** exp if base is not None and exp is not None else None
        # TODO: log to DB
        return jsonify({"operation": "pow", "base": base, "exp": exp, "result": result})

    @app.route("/factorial")
    def compute_factorial():
        n = request.args.get("n", type=int)
        result = None
        if n is not None and n >= 0:
            result = 1
            for i in range(2, n+1):
                result *= i
        # TODO: log to DB
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
        # TODO: log to DB
        return jsonify({"operation": "fibonacci", "n": n, "result": result})

    @app.route("/logs")
    def get_logs():
        # TODO: fetch logs from DB
        return jsonify([])

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5002, debug=True)
