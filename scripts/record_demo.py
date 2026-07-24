#!/usr/bin/env python3
"""Auto-record a 3-minute LineageGuard demo video by driving macOS UI."""

import os
import subprocess
import time
from pathlib import Path

DEMO_DIR = Path("/Users/radik/hackathons/datahub-lineageguard/demo_video")
DEMO_DIR.mkdir(parents=True, exist_ok=True)


def run_in_terminal(cmd: str) -> None:
    escaped = cmd.replace('"', '\\"')
    script = f'tell application "Terminal" to do script "{escaped}"'
    subprocess.run(["osascript", "-e", script], check=True)


def activate_terminal() -> None:
    subprocess.run(["osascript", "-e", 'tell application "Terminal" to activate'], check=True)


def open_url(url: str) -> None:
    subprocess.run(["open", url], check=True)


def main():
    video_path = DEMO_DIR / "demo_live.mp4"
    log_path = DEMO_DIR / "demo_live.log"

    # Start screen recording
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-f", "avfoundation", "-i", "0", "-t", "180",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video_path), "-y"],
        stdout=subprocess.DEVNULL, stderr=open(log_path, "w"),
    )
    print(f"Recording started, pid={ffmpeg.pid}")

    try:
        # 0:00-0:15: intro
        run_in_terminal('cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && printf "%s\\n" "LineageGuard: ML Supply Chain Security Agent for DataHub" "Repo: https://github.com/RadikHoroshev/datahub-lineageguard"')
        time.sleep(15)

        # 0:15-0:45: ingest
        run_in_terminal('cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && python -m lineageguard.ingest')
        time.sleep(30)

        # 0:45-1:30: real scan
        run_in_terminal('cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && python -m lineageguard.run_real')
        time.sleep(45)

        # 1:30-2:20: DataHub UI
        open_url("http://localhost:9002")
        time.sleep(50)

        # 2:20-2:50: Streamlit UI
        open_url("http://localhost:8501")
        time.sleep(30)

        # 2:50-3:00: final summary
        activate_terminal()
        run_in_terminal('cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && printf "%s\\n" "LineageGuard demo complete" "Submit: https://devpost.com/software/lineageguard-tmvhr4"')
        time.sleep(10)
    finally:
        ffmpeg.wait(timeout=60)

    print(f"Demo video saved to {video_path}")


if __name__ == "__main__":
    main()
