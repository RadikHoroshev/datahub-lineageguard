#!/usr/bin/env python3
"""Open a persistent Chrome window that the agent can control later.

Run this once, log in to YouTube / Devpost manually in the opened window,
then close it. The profile is saved under ~/.hermes/browser-profiles/chrome-agent
and can be reused by the agent for automation.

For future agent-controlled sessions, run:
    python scripts/agent_browser.py <url>
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / ".hermes" / "browser-profiles" / "chrome-agent"


def main():
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
        page.goto("https://www.youtube.com/upload")
        print("Chrome opened with agent profile.")
        print("Log in to YouTube if needed, then close the browser window.")
        print(f"Profile saved to: {PROFILE_DIR}")
        input("Press Enter after you close the browser...")
        browser.close()


if __name__ == "__main__":
    main()
