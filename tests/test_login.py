import os
import subprocess
import sys
import time
import urllib.request
from uuid import uuid4

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "http://127.0.0.1:5001"


@pytest.fixture(scope="module")
def flask_server():
    environment = os.environ.copy()
    environment["PORT"] = "5001"
    server = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    for _ in range(30):
        try:
            urllib.request.urlopen(BASE_URL + "/login", timeout=1)
            break
        except (urllib.error.URLError, ConnectionError):
            time.sleep(0.5)
    else:
        server.terminate()
        raise RuntimeError("Flask server did not start")

    yield
    server.terminate()
    server.wait(timeout=10)


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,720")
    try:
        driver = webdriver.Chrome(options=options)
    except NoSuchDriverException as error:
        pytest.skip(
            "ChromeDriver is unavailable. Install Google Chrome and ChromeDriver "
            "or allow Selenium Manager to download them."
        )
    yield driver
    driver.quit()


def test_login_logout_and_invalid_credentials(flask_server, browser):
    wait = WebDriverWait(browser, 10)
    email = f"selenium-{uuid4().hex}@example.com"
    password = "correct-password"

    browser.get(BASE_URL + "/register")
    browser.find_element(By.ID, "name").send_keys("Selenium Member")
    browser.find_element(By.ID, "email").send_keys(email)
    browser.find_element(By.ID, "password").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.url_contains("/login"))
    browser.find_element(By.ID, "email").send_keys(email)
    browser.find_element(By.ID, "password").send_keys(password)
    browser.find_element(By.ID, "login-button").click()

    wait.until(EC.url_to_be(BASE_URL + "/"))
    assert "Welcome, Selenium Member!" in browser.page_source

    browser.find_element(By.LINK_TEXT, "Log out").click()
    wait.until(EC.url_contains("/login"))

    browser.find_element(By.ID, "email").send_keys(email)
    browser.find_element(By.ID, "password").send_keys("wrong-password")
    browser.find_element(By.ID, "login-button").click()

    error = wait.until(EC.visibility_of_element_located((By.ID, "login-error")))
    assert error.text == "Invalid email or password."
