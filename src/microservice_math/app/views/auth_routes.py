from flask import Blueprint, request, session, redirect, url_for, render_template_string
from app.models.user import User

users = {"test": User("test", "test")}
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
        user = users.get(username)
        print(username, password)  # Debugging line to check credentials
        print(user.check_password(password))
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('root'))
        else:
            error = 'Invalid credentials'
    return render_template_string(login_page, error=error)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            error = 'User already exists'
        else:
            users[username] = User(username, password)
            return redirect(url_for('auth.login'))
    return render_template_string(login_page, error=error)

@auth_blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
