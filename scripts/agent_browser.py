#!/usr/bin/env python3
"""Agent-controlled Chrome using a persistent profile.

Usage:
    python scripts/agent_browser.py https://www.youtube.com/upload

The profile is shared with scripts/open_chrome_agent.py so that manual logins
persist across sessions.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / ".hermes" / "browser-profiles" / "chrome-agent"


def navigate(url: str):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )
        page = browser.new_page()
        page.goto(url)
        print(f"Opened {url} in agent-controlled Chrome.")
        print("Close the browser when done.")
        input("Press Enter after you close the browser...")
        browser.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/upload"
    navigate(url)
