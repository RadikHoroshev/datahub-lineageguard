# 3-Minute Demo Video Script — LineageGuard

## Goal

Show judges that LineageGuard:
1. Uses DataHub's end-to-end ML lineage
2. Detects real ML supply-chain risks
3. Works through CLI, API, and UI
4. Is easy to reproduce from the public repo

## Scene breakdown (~3:00 total)

### 0:00–0:20 — Hook + problem

> "ML pipelines fail silently. A poisoned dataset, a shadow model, or the wrong model version deployed to production can cost you weeks before any metric looks off. The problem isn't observability — it's that the risk lives in the lineage graph between your data, features, model, and endpoint."

Show a simple diagram:
```
Dataset → Features → Feature Table → Model → Endpoint
```

### 0:20–0:40 — Solution

> "LineageGuard is an agent that reads DataHub's ML lineage and flags four concrete risks: tainted datasets, version mismatch, shadow models, and missing lineage."

Show the GitHub repo homepage.

### 0:40–1:20 — Setup + DataHub seed

Terminal commands (speak while typing):
```bash
pip install acryl-datahub
datahub docker quickstart
python -m lineageguard.ingest
```

Show DataHub UI at http://localhost:9002 with the seeded fraud-detection lineage graph.

### 1:20–1:50 — CLI scan

Terminal:
```bash
python -m lineageguard.run_real
```

Show the JSON report with 3 anomalies:
- critical: tainted dataset
- high: version mismatch v1.2.3 → v1.2.1
- medium: shadow model

### 1:50–2:20 — Streamlit UI

Terminal:
```bash
streamlit run lineageguard/app.py
```

Browser at http://localhost:8501. Click **Scan Lineage**. Show metrics and anomaly cards.

### 2:20–2:50 — Architecture + tech

> "The agent talks to DataHub over GraphQL, walks upstream and downstream lineage, and runs rule-based detectors. It exposes CLI, FastAPI, and Streamlit interfaces. The repo is Apache 2.0 and includes pytest tests plus a synthetic pipeline for reproducible demos."

Show file tree / README.

### 2:50–3:00 — Close

> "LineageGuard turns DataHub lineage into ML supply-chain security. Repo, setup instructions, and sample output are at github.com/RadikHoroshev/datahub-lineageguard."

## Recording tips

- Use macOS QuickTime (`Cmd+Shift+5`) or OBS
- Record terminal + browser side-by-side or sequential
- Keep terminal font large (14–16pt)
- Avoid sensitive info on screen
- Export to 1080p, upload to YouTube as Unlisted or Public

## Commands to have ready

```bash
cd /Users/radik/hackathons/datahub-lineageguard
source .venv/bin/activate
datahub docker quickstart        # should already be running
python -m lineageguard.ingest    # if needed
python -m lineageguard.run_real
streamlit run lineageguard/app.py
```
