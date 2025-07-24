from flask import Flask, session, redirect, url_for
import asyncio

from .db import init_db
from .views.math_routes import math_blueprint
from .views.auth_routes import auth_blueprint

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"  
    app.register_blueprint(math_blueprint, url_prefix="/math")
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    @app.route("/")
    def root():
        if not ("username" in session):
            return redirect(url_for("auth.login"))
        return {"message": f"Math microservice running for {session['username']}..."}

    return app

if __name__ == "__main__":
    asyncio.run(init_db())
    app = create_app()
    app.run(debug=True)