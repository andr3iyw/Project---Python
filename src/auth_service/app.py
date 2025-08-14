# auth_service/app.py
from flask import Flask, request, jsonify, render_template_string
import asyncio
import os
import time
import jwt  # PyJWT
from db import init_db

# ====== CONFIG ======
JWT_SECRET = os.getenv("AUTH_JWT_SECRET", "super-secret-jwt-key")  # set in env for production
JWT_ALG = "HS256"
JWT_TTL_SECONDS = int(os.getenv("AUTH_JWT_TTL_SECONDS", "86400"))  # 24h

def create_jwt(username: str) -> str:
    now = int(time.time())
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + JWT_TTL_SECONDS,
        "iss": "auth_service",
        "scope": "user"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def create_app():
    app = Flask(__name__)
    app.secret_key = "authsecretkey"  # not used for sessions anymore

    # Simple HTML helper for manual testing (optional)
    login_page = """
    <!doctype html>
    <title>Login</title>
    <h2>Login</h2>
    <form method="post" action="/login">
      <div>Username: <input type="text" name="username"></div>
      <div>Password: <input type="password" name="password"></div>
      <button type="submit">Login</button>
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    {% if token %}
      <p><b>Token (copy this):</b></p>
      <textarea cols="80" rows="6">{{ token }}</textarea>
    {% endif %}
    """

    @app.get("/login")
    def login_get():
        # Render a tiny form for manual testing
        return render_template_string(login_page)

    @app.post("/login")
    def login_post():
        """
        Accepts either form or JSON:
        - form: username, password
        - json: {"username": "...", "password": "..."}
        Returns: {"access_token": "<JWT>", "token_type": "bearer", "username": "..."}
        """
        from models.user import verify_user
        from db import get_db_connection

        # Accept both content types
        if request.is_json:
            data = request.get_json(silent=True) or {}
            username = data.get("username", "").strip()
            password = data.get("password", "")
        else:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

        if not username or not password:
            # HTML form vs API JSON response
            if request.is_json:
                return jsonify({"error": "Username and password cannot be empty."}), 400
            return render_template_string(login_page, error="Username and password cannot be empty.")

        async def check_login():
            db = await get_db_connection()
            valid = await verify_user(db, username, password)
            await db.close()
            return valid

        valid = asyncio.run(check_login())
        if not valid:
            if request.is_json:
                return jsonify({"error": "Invalid credentials"}), 401
            return render_template_string(login_page, error="Invalid credentials")

        token = create_jwt(username)
        if request.is_json:
            return jsonify({"access_token": token, "token_type": "bearer", "username": username})

        # For the HTML page, just show the token
        return render_template_string(login_page, token=token)

    @app.post("/register")
def register():
    from models.user import create_user, get_user
    from db import get_db_connection

    if request.is_json:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
    else:
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password cannot be empty."}), 400

    async def do_register():
        db = await get_db_connection()
        user = await get_user(db, username)
        if user:
            await db.close()
            return False
        await create_user(db, username, password)
        await db.close()
        return True

    success = asyncio.run(do_register())
    if not success:
        return jsonify({"error": "User already exists"}), 409

    # If you're on the JWT flow, you can issue a token here:
    # token = create_jwt(username)
    # return jsonify({"message":"User created","access_token":token,"token_type":"bearer","username":username}), 201
    return jsonify({"message": "User created", "username": username}), 201

    # Optional health
    @app.get("/health")
    def health():
        return {"status": "ok", "service": "auth_service"}

    return app


if __name__ == "__main__":
    asyncio.run(init_db())  # Initialize the database
    app = create_app()
    print("auth_service started")
    app.run(host="0.0.0.0", port=5001, debug=True)
