import os
import sqlite3

from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "beginner-library-secret-key"
DATABASE = "library.db"


def calculate_fine(overdue_days):
    if overdue_days < 0:
        raise ValueError("Overdue days cannot be negative")
    return overdue_days * 5


def setup_database():
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS books ("
            "id INTEGER PRIMARY KEY, title TEXT, author TEXT, available INTEGER)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS members ("
            "id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)"
        )
        if db.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO books (title, author, available) VALUES (?, ?, ?)",
                [
                    ("The Alchemist", "Paulo Coelho", 1),
                    ("Wings of Fire", "A. P. J. Abdul Kalam", 1),
                    ("Pride and Prejudice", "Jane Austen", 0),
                ],
            )


@app.route("/")
def index():
    search = request.args.get("search", "").strip().lower()
    with sqlite3.connect(DATABASE) as db:
        db.row_factory = sqlite3.Row
        books = db.execute("SELECT * FROM books ORDER BY title").fetchall()
    if search:
        books = [book for book in books if search in book["title"].lower()]
    return render_template(
        "index.html",
        books=books,
        search_text=search,
        member_name=session.get("member_name"),
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            with sqlite3.connect(DATABASE) as db:
                db.execute(
                    "INSERT INTO members (name, email, password) VALUES (?, ?, ?)",
                    (
                        request.form["name"],
                        request.form["email"].strip().lower(),
                        generate_password_hash(request.form["password"]),
                    ),
                )
        except sqlite3.IntegrityError:
            return render_template(
                "register.html", message="Email is already registered."
            )
        return redirect("/login")
    return render_template("register.html", message="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        with sqlite3.connect(DATABASE) as db:
            member = db.execute(
                "SELECT name, password FROM members WHERE email = ?",
                (request.form["email"].strip().lower(),),
            ).fetchone()
        if member and check_password_hash(member[1], request.form["password"]):
            session["member_name"] = member[0]
            return redirect("/")
        return render_template("login.html", message="Invalid email or password.")
    return render_template("login.html", message="")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    setup_database()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        use_reloader=False,
    )
