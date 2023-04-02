from flask import Flask, redirect, url_for, render_template, request, flash

app = Flask(__name__)
app.secret_key = "my_secret_key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "hjh" and password == "123":
            return redirect("http://127.0.0.1:7860")
        else:
            error = 'Invalid username or password!'
            return render_template('login.html', error=error)
    return render_template("login.html")


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


if __name__ == "__main__":
    app.run(debug=True)
