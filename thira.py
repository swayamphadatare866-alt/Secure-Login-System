from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "mysecretkey"

bcrypt = Bcrypt(app)

# -----------------------------
# Database
# -----------------------------
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

conn.commit()
conn.close()

# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        hashed_password=bcrypt.generate_password_hash(password).decode("utf-8")

        conn=sqlite3.connect("database.db")
        cursor=conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username,hashed_password)
            )
            conn.commit()

        except:
            conn.close()
            return "Username already exists."

        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        conn=sqlite3.connect("database.db")
        cursor=conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user=cursor.fetchone()

        conn.close()

        if user:

            if bcrypt.check_password_hash(user[2],password):

                session["user"]=username

                return redirect("/dashboard")

        return "Invalid Username or Password"

    return render_template("login.html")

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", user=session["user"])

# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.pop("user",None)

    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)
    
