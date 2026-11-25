
from flask import Flask, render_template_string, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Create database
def create_table():
    con = sqlite3.connect("users.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    con.commit()
    con.close()

# Register page
register_page = """
<h2>Register</h2>
<form method="POST">
    <input name="username" placeholder="Username" required><br><br>
    <input type="password" name="password" placeholder="Password" required><br><br>
    <button type="submit">Register</button>
</form>
<a href="/login">Login</a>
"""

# Login page
login_page = """
<h2>Login</h2>
<form method="POST">
    <input name="username" placeholder="Username" required><br><br>
    <input type="password" name="password" placeholder="Password" required><br><br>
    <button type="submit">Login</button>
</form>
<a href="/register">Register</a>
"""

# Home page
home_page = """
<h2>Welcome {{ username }}!</h2>
<p>You are successfully logged in.</p>
<a href="/logout">Logout</a>
"""

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or len(password) < 6:
            return "Enter username and password (minimum 6 characters)"

        hashed_password = generate_password_hash(password)

        try:
            con = sqlite3.connect("users.db")
            con.execute(
                "INSERT INTO users(username, password) VALUES(?, ?)",
                (username, hashed_password)
            )
            con.commit()
            con.close()
            return "Registration successful! <a href='/login'>Login</a>"
        except sqlite3.IntegrityError:
            return "Username already exists!"

    return render_template_string(register_page)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        con = sqlite3.connect("users.db")
        user = con.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        con.close()

        if user and check_password_hash(user[2], password):
            session["username"] = username
            return redirect("/home")

        return "Invalid username or password!"

    return render_template_string(login_page)

# Home
@app.route("/home")
def home():
    if "username" in session:
        return render_template_string(
            home_page, username=session["username"]
        )
    return redirect("/login")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    create_table()
    app.run(debug=True)
