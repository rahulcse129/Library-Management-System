# Library Management System

A beginner-friendly Flask application for the college practical examination.

## Initial setup

1. Create and activate a Python virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the project dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

3. Start the Flask application:

   ```powershell
   py app.py
   ```

4. Open http://localhost:5000 in a browser.

The home page provides a simple title search over sample books stored in SQLite.

The member pages are available at `/register` and `/login`.

## Run PyTest

Run the automated fine-calculation tests:

```powershell
pytest -v
```

The tests cover zero overdue days, five overdue days, one overdue day, and
negative overdue days.

## Run Selenium tests

Install Google Chrome and make sure it is available. Selenium 4 uses Selenium
Manager to obtain a compatible ChromeDriver automatically. Start the tests
with:

```powershell
pytest -v tests/test_login.py
```

The Selenium test registers a temporary member, logs in with valid
credentials, logs out, and checks the invalid-credentials message.

## Docker

Build and run the application:

```powershell
docker build -t library-app .
docker run -d -p 5000:5000 --name library-container library-app
```

Open http://localhost:5000 in a browser. Use `docker ps` to list running
containers, `docker logs library-container` to read application logs, and
`docker stop library-container` to stop the container.

## GitHub Actions

The workflow in `.github/workflows/python-app.yml` runs when code is pushed to
the `main` branch. It installs the dependencies and checks that `app.py` has
valid Python syntax. Open the repository on GitHub and select **Actions** to
see whether the workflow passed or failed.
