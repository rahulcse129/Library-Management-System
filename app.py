import sqlite3
from pathlib import Path

from flask import Flask, render_template, request


app = Flask(__name__)
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


@app.route("/")
def index():
    search_text = request.args.get("search", "").strip()
    books = get_books()

    if search_text:
        books = [
            book for book in books if search_text.lower() in book["title"].lower()
        ]

    return render_template("index.html", books=books, search_text=search_text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
