#!/usr/bin/env bash
# Auto-generate a 3-minute LineageGuard demo video by driving macOS UI.

set -e

DEMO_DIR="/Users/radik/hackathons/datahub-lineageguard/demo_video"
mkdir -p "$DEMO_DIR"

# Start screen recording in background
ffmpeg -f avfoundation -i "0" -t 180 -pix_fmt yuv420p -movflags +faststart "$DEMO_DIR/demo_live.mp4" -y 2> "$DEMO_DIR/demo_live.log" &
FFMPEG_PID=$!
echo "Recording started, pid=$FFMPEG_PID"

# Helper: activate and run Terminal command
run_in_terminal() {
    local cmd="$1"
    osascript <<EOF
tell application "Terminal"
    activate
    do script "$cmd"
end tell
EOF
}

# 0:00 - 0:15: Terminal intro
run_in_terminal 'cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && printf "%s\n" "LineageGuard: ML Supply Chain Security Agent for DataHub" "Repo: https://github.com/RadikHoroshev/datahub-lineageguard"'
sleep 15

# 0:15 - 0:45: Show ingest
run_in_terminal 'cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && python -m lineageguard.ingest'
sleep 30

# 0:45 - 1:30: Run real DataHub scan
run_in_terminal 'cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && python -m lineageguard.run_real'
sleep 45

# 1:30 - 2:20: Open DataHub UI lineage graph
open http://localhost:9002
sleep 50

# 2:20 - 2:50: Open Streamlit UI
open http://localhost:8501
sleep 30

# 2:50 - 3:00: Final terminal summary
run_in_terminal 'cd /Users/radik/hackathons/datahub-lineageguard && source .venv/bin/activate && clear && printf "%s\n" "LineageGuard demo complete" "Submit: https://devpost.com/software/lineageguard-tmvhr4"'
sleep 10

# Wait for ffmpeg to finish
wait $FFMPEG_PID || true

echo "Demo video saved to $DEMO_DIR/demo_live.mp4"
