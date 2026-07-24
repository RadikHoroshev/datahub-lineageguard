# LineageGuard — 3-minute demo script

## Prerequisites (already running on Mac mini demo machine)

| Service | URL | Creds |
|--|--|--|
| DataHub UI | http://localhost:9002 | `datahub` / `datahub` |
| Streamlit | http://localhost:8501 | — |
| GMS API | http://localhost:8080 | — |

## One-command synthetic demo (no UI)

```bash
cd /Users/radik/hackathons/datahub-lineageguard
source .venv/bin/activate
python -m lineageguard.cli --demo --output /tmp/lineageguard_report.json
cat /tmp/lineageguard_report.json | python -m json.tool | head -80
```

## Live DataHub scan

```bash
source .venv/bin/activate
# ensure synthetic pipeline is ingested once:
python -m lineageguard.ingest
# scan real lineage
python -m lineageguard.run_real
```

Expected anomalies (demo data):

1. **version_mismatch (high)** — fraud-detection-model v1.2.3 deployed as v1.2.1  
2. **tainted_dataset (critical)** — transactions-v2-poisoned infects downstream assets  
3. **shadow_model (medium)** — unregistered shadow-fraud-model  

## Streamlit (judges click)

1. Open http://localhost:8501  
2. Click **Scan Lineage**  
3. Show findings table + risk summary  
4. Optional: open DataHub http://localhost:9002 and show the same assets  

## FastAPI

```bash
uvicorn lineageguard.api:app --host 127.0.0.1 --port 8000
# GET http://127.0.0.1:8000/docs
```

## 3-minute video outline

| Time | Shot |
|--|--|
| 0:00–0:30 | Problem: silent ML supply-chain failures |
| 0:30–1:00 | Architecture: DataHub lineage → agent → report |
| 1:00–2:00 | Live: Streamlit Scan Lineage → 3 anomalies |
| 2:00–2:30 | CLI `run_real` + JSON report evidence |
| 2:30–3:00 | Why DataHub: graph truth, tags path, next steps |

## Unit tests (CI-safe)

```bash
pytest tests/test_agent.py -q
```
