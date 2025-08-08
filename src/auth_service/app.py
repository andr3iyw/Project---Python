from flask import Flask
from db import init_db
import asyncio


def create_app():
    app = Flask(__name__)
    app.secret_key = "authsecretkey"

    login_page = """
    <!doctype html>
    <title>Login</title>
    <h2>Login</h2>
    <form method="post">
      Username: <input type="text" name="username"><br>
      Password: <input type="password" name="password"><br>
      <input type="submit" value="Login">
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    """

    @app.route("/login", methods=["GET", "POST"])
    def login():
        from flask import (
            request,
            session,
            redirect,
            url_for,
            render_template_string,
        )
        import asyncio

        error = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if not username or not password:
                error = "Username and password cannot be empty."
            else:
                from models.user import verify_user
                from db import get_db_connection

                async def check_login():
                    db = await get_db_connection()
                    valid = await verify_user(db, username, password)
                    await db.close()
                    return valid

                valid = asyncio.run(check_login())
                if valid:
                    session["username"] = username
                    return redirect(url_for("login"))
                else:
                    error = "Invalid credentials"
        return render_template_string(login_page, error=error)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        from flask import request, redirect, url_for, render_template_string
        import asyncio

        error = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if not username or not password:
                error = "Username and password cannot be empty."
            else:
                from models.user import create_user, get_user
                from db import get_db_connection

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
                    error = "User already exists"
                else:
                    return redirect(url_for("login"))
        return render_template_string(login_page, error=error)

    @app.route("/logout")
    def logout():
        from flask import session, redirect, url_for

        session.pop("username", None)
        return redirect(url_for("login"))

    return app


if __name__ == "__main__":
    asyncio.run(init_db())  # Initialize the database
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
