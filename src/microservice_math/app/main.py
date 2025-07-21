from flask import Flask
import asyncio

from app.db import init_db
from app.views.math_routes import math_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(math_blueprint, url_prefix="/math")

    @app.route("/")
    def root():
        return {"message": "Math microservice running..."}

    return app

if __name__ == "__main__":
    asyncio.run(init_db())
    app = create_app()
    app.run(debug=True)