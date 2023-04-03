from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "my_secret_key"
# 设置session的保留时间为1天
app.permanent_session_lifetime = timedelta(days=1)

LOGIN_KEY = "logged_in"
USERNAME_KEY = "username"


@app.route("/check_login", methods=["GET"])
def check_login():
    data = {LOGIN_KEY: False}

    if LOGIN_KEY in session and USERNAME_KEY in session:
        data = {LOGIN_KEY: True, USERNAME_KEY: session[USERNAME_KEY]}
        return jsonify(data)

    return jsonify(data)


def label_login(username):
    session[LOGIN_KEY] = True
    session[USERNAME_KEY] = username


def clean_login():
    session.pop(LOGIN_KEY, None)
    session.pop(USERNAME_KEY, None)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "hjh" and password == "123":
            label_login(username)
            return redirect("http://127.0.0.1:8089")
        else:
            error = 'Invalid username or password!'
            return render_template('login.html', error=error)
    return render_template("login.html")


@app.route('/profile')
def profile():
    # 从 session 中获取信息
    username = session.get(USERNAME_KEY, None)
    logged_in = session.get(LOGIN_KEY, False)
    data = {LOGIN_KEY: logged_in, USERNAME_KEY: username}
    return jsonify(data)


@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # if username in users:
        #     error = "Username already taken"
        #     return render_template('signup.html', error=error)
        # else:
        #     users[username] = password
        #     return redirect(url_for('dashboard'))
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop(LOGIN_KEY, None)
    return 'You are now logged out'


if __name__ == "__main__":
    app.run(debug=True)
