#!/usr/bin/env python3
"""Record a clean full-screen Terminal demo video for LineageGuard."""

import subprocess
import time
from pathlib import Path

DEMO_DIR = Path('/Users/radik/hackathons/datahub-lineageguard/demo_video')
DEMO_DIR.mkdir(exist_ok=True)
OUTPUT = DEMO_DIR / 'demo_clean.mp4'


def send_to_terminal(cmd: str) -> None:
    """Send a command to the front Terminal window."""
    escaped = cmd.replace('"', '\\"')
    script = f'tell application "Terminal" to do script "{escaped}" in front window'
    subprocess.run(["osascript", "-e", script], check=True)


def clear_terminal() -> None:
    send_to_terminal("clear")


def set_clean_prompt() -> None:
    send_to_terminal('export PS1="> "')


def type_command(cmd: str, wait: int = 2) -> None:
    send_to_terminal(cmd)
    time.sleep(wait)


def main():
    # Make sure Terminal is frontmost and full screen
    subprocess.run([
        "osascript", "-e",
        'tell application "Terminal" to activate'
    ], check=True)
    time.sleep(1)

    # Set clean prompt and cd
    set_clean_prompt()
    send_to_terminal("cd /Users/radik/hackathons/datahub-lineageguard")
    send_to_terminal("source .venv/bin/activate")
    clear_terminal()

    # Start ffmpeg recording of full screen, will crop to terminal area later
    # For now record full screen and crop post-process
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-f", "avfoundation", "-i", "0", "-t", "160",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(DEMO_DIR / "demo_clean_raw.mp4"), "-y"],
        stdout=subprocess.DEVNULL,
        stderr=open(DEMO_DIR / "demo_clean.log", "w"),
    )
    print(f"Recording started, pid={ffmpeg.pid}")

    try:
        time.sleep(2)

        # Scene 1: Title (0:00-0:15)
        clear_terminal()
        send_to_terminal(r'printf "%s\n" "" "LineageGuard" "ML Supply Chain Security Agent for DataHub" "" "Challenge: Production ML Agents"')
        time.sleep(12)

        # Scene 2: Problem (0:15-0:35)
        clear_terminal()
        send_to_terminal(r'printf "%s\n" "" "ML pipelines fail silently:" "" "  * Poisoned training data" "  * Wrong model version deployed" "  * Shadow / unregistered models" "  * Missing lineage"')
        time.sleep(18)

        # Scene 3: Solution (0:35-0:55)
        clear_terminal()
        send_to_terminal(r'printf "%s\n" "" "LineageGuard reads DataHub lineage" "and detects:" "" "  TAINTED_DATASET" "  VERSION_MISMATCH" "  SHADOW_MODEL" "  MISSING_LINEAGE"')
        time.sleep(18)

        # Scene 4: Ingest (0:55-1:15)
        clear_terminal()
        type_command("python -m lineageguard.ingest", wait=18)

        # Scene 5: Scan (1:15-1:50)
        clear_terminal()
        type_command("python -m lineageguard.run_real", wait=32)

        # Scene 6: Results summary (1:50-2:20)
        clear_terminal()
        send_to_terminal(r'printf "%s\n" "" "Scan Results:" "" "  [CRITICAL] Tainted dataset feeds 5 downstream assets" "  [HIGH]     Model v1.2.3 deployed as v1.2.1" "  [MEDIUM]   Shadow model unregistered"')
        time.sleep(25)

        # Scene 7: Outputs (2:20-2:40)
        clear_terminal()
        send_to_terminal(r'printf "%s\n" "" "Outputs:" "" "  * JSON report" "  * Markdown explanation" "  * Streamlit UI" "  * FastAPI endpoint"')
        time.sleep(18)

        # Scene 8: Close (2:40-2:55)
        clear_terminal()
        send_to_terminal(r'printf "%s\n" "" "github.com/RadikHoroshev/datahub-lineageguard" "devpost.com/software/lineageguard-tmvhr4"')
        time.sleep(15)

    finally:
        ffmpeg.wait(timeout=60)

    # Crop to terminal area (assuming 1920x1080 full screen, Terminal full screen)
    # Terminal full screen occupies roughly whole screen; crop top menu bar (0,25 to 1920,1080)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(DEMO_DIR / "demo_clean_raw.mp4"),
        "-vf", "crop=1920:1055:0:25",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(OUTPUT)
    ], check=True)

    print(f"Clean demo saved to {OUTPUT}")


if __name__ == "__main__":
    main()
