import os
import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = "beginner-library-secret-key"
DATABASE = Path(__file__).with_name("library.db")


def calculate_fine(overdue_days):
    if overdue_days < 0:
        raise ValueError("Overdue days cannot be negative")
    return overdue_days * 5


def get_books():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            available INTEGER NOT NULL
        )
        """
    )

    book_count = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if book_count == 0:
        connection.executemany(
            "INSERT INTO books (title, author, available) VALUES (?, ?, ?)",
            [
                ("The Alchemist", "Paulo Coelho", 1),
                ("Wings of Fire", "A. P. J. Abdul Kalam", 1),
                ("Pride and Prejudice", "Jane Austen", 0),
            ],
        )
        connection.commit()

    books = connection.execute(
        "SELECT id, title, author, available FROM books ORDER BY title"
    ).fetchall()
    connection.close()
    return books


def create_members_table():
    connection = sqlite3.connect(DATABASE)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


@app.route("/")
def index():
    search_text = request.args.get("search", "").strip()
    books = get_books()

    if search_text:
        books = [
            book for book in books if search_text.lower() in book["title"].lower()
        ]

    return render_template(
        "index.html",
        books=books,
        search_text=search_text,
        member_name=session.get("member_name"),
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        create_members_table()

        connection = sqlite3.connect(DATABASE)
        try:
            connection.execute(
                "INSERT INTO members (name, email, password) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            message = "A member with this email already exists."
            connection.close()
            return render_template("register.html", message=message)
        connection.close()
        return redirect(url_for("login"))

    return render_template("register.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        create_members_table()

        connection = sqlite3.connect(DATABASE)
        member = connection.execute(
            "SELECT name, password FROM members WHERE email = ?", (email,)
        ).fetchone()
        connection.close()

        if member and check_password_hash(member[1], password):
            session["member_name"] = member[0]
            return redirect(url_for("index"))
        message = "Invalid email or password."

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    create_members_table()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
        use_reloader=False,
    )
