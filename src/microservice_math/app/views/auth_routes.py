
from flask import Blueprint, request, session, redirect, url_for, render_template_string
import asyncio
from app.models.user import create_user, verify_user, get_user
from app.db import get_db_connection

auth_blueprint = Blueprint('auth', __name__)

login_page = '''
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post">
  Username: <input type="text" name="username"><br>
  Password: <input type="password" name="password"><br>
  <input type="submit" value="Login">
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
'''

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            error = 'Username and password cannot be empty.'
        else:
            async def check_login():
                db = await get_db_connection()
                valid = await verify_user(db, username, password)
                await db.close()
                return valid
            valid = asyncio.run(check_login())
            if valid:
                session['username'] = username
                return redirect(url_for('auth.login'))
            else:
                error = 'Invalid credentials'
    return render_template_string(login_page, error=error)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            error = 'Username and password cannot be empty.'
        else:
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
                error = 'User already exists'
            else:
                return redirect(url_for('auth.login'))
    return render_template_string(login_page, error=error)

@auth_blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
