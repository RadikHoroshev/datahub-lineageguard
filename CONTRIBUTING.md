# Contributing & Demo

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/test_agent.py -q
```

## Streamlit demo

```bash
source .venv/bin/activate
streamlit run lineageguard/app.py
# http://localhost:8501 → Scan Lineage
```

If DataHub GMS is not reachable at `http://localhost:8080`, the UI falls back to synthetic demo data.

## Live DataHub

```bash
datahub docker quickstart
# UI http://localhost:9002  (datahub / datahub)

python -m lineageguard.ingest      # load synthetic ML pipeline once
python -m lineageguard.run_real    # scan live lineage
```

## FastAPI

```bash
uvicorn lineageguard.api:app --host 127.0.0.1 --port 8000
```

## Tests

```bash
pytest tests/ -q
```

CI runs unit tests only (no Docker/DataHub required).

## Pull requests

- Keep anomaly detector semantics stable unless tests are updated.
- Do not commit `.venv/`, secrets, or DataHub volume data.
- Prefer small PRs with a clear Demo/CI path.
