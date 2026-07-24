"""Open a persistent Playwright browser for Devpost login.

Run this script, log in to Devpost manually in the opened browser,
then close it. The profile will retain cookies/session for later use.
"""

from playwright.sync_api import sync_playwright
import time

PROFILE_DIR = "/Users/radik/.hermes/browser-profiles/devpost"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        PROFILE_DIR,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = browser.new_page()
    page.goto("https://secure.devpost.com/users/login")
    print("Browser opened. Log in to Devpost, then close the browser window.")
    print("Profile saved to:", PROFILE_DIR)
    while len(browser.pages) > 0:
        time.sleep(1)
    browser.close()
