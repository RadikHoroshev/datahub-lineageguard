# Recording the 3-minute demo (quick checklist)

## Capture tools (pick one)

```bash
# macOS built-in
# Cmd+Shift+5 → Record Selected Portion
```

Or QuickTime Player → New Screen Recording.

## Sequence

1. **Terminal (20s)** — `pytest tests/test_agent.py -q` green  
2. **DataHub (40s)** — http://localhost:9002 show fraud-detection / transactions assets  
3. **Streamlit (60s)** — http://localhost:8501 → Scan Lineage → highlight 3 findings  
4. **Terminal (40s)** — `python -m lineageguard.run_real` + open report snippet  
5. **Close (20s)** — repo URL + “Apache 2.0 · open source”

## Export

- 1080p, ≤3:00, mp4  
- Upload to YouTube/unlisted or Devpost video field  
- Filename: `lineageguard-demo-3min.mp4`
