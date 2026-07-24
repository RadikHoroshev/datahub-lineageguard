# LineageGuard: ML Supply Chain Security Agent for DataHub

An AI agent that protects ML pipelines by analyzing DataHub's end-to-end lineage graph.

## Problem

ML systems fail silently. Data poisoning, shadow models, and model-version drift propagate through pipelines undetected because the link between training data, features, models, and endpoints is invisible. DataHub makes that link visible — LineageGuard makes it actionable.

## What it does

LineageGuard reads the ML lineage graph from DataHub (training datasets → features → feature tables → models → deployment endpoints) and detects security and reliability anomalies:

- **Tainted datasets** — datasets tagged `tainted` or `poisoned` that feed production features or models
- **Version mismatch** — deployed model version differs from the trained model version in the lineage
- **Shadow models** — unregistered or untracked models with lineage to production assets
- **Missing lineage** — models or feature tables with no upstream provenance

It outputs a structured JSON report, a human-readable Markdown explanation, and (optionally) an LLM-generated risk narrative.

## Why DataHub

LineageGuard uses DataHub as the single source of truth:

- Reads upstream/downstream lineage via DataHub's GraphQL API
- Stores pipeline metadata as DataHub datasets with custom properties and tags
- Can write security findings back into DataHub as tags, assertions, or alerts (roadmap)

It targets **Challenge 3** of the [Build with DataHub: The Agent Hackathon](https://datahub.devpost.com/): *Build agents for ML teams that protect models in production.*

## Quick start

### 1. Install DataHub locally

```bash
pip install acryl-datahub
datahub docker quickstart
```

Open http://localhost:9002 and log in with `datahub` / `datahub`.

### 2. Clone and set up the project

```bash
git clone https://github.com/<your-user>/lineageguard-datahub.git
cd lineageguard-datahub
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Seed the demo ML pipeline into DataHub

```bash
python -m lineageguard.ingest
```

### 4. Run a security scan

```bash
python -m lineageguard.run_real
```

Expected output: a JSON report with three detected anomalies — version mismatch, tainted dataset, and shadow model.

### 5. Launch the Streamlit demo

```bash
streamlit run lineageguard/app.py
```

Open http://localhost:8501, enter a seed URN (default provided), and click **Scan Lineage**.

### 6. Run tests

```bash
pytest tests/test_agent.py -q
```

## Project structure

```
lineageguard/
  agent.py          # Anomaly detection engine
  datahub_client.py # DataHub GraphQL/REST client
  ingest.py         # Seed synthetic ML pipeline into DataHub
  run_real.py       # End-to-end DataHub scan
  api.py            # FastAPI server
  app.py            # Streamlit UI
  cli.py            # Command-line interface
  demo_data.py      # Synthetic pipeline for tests
  explainer.py      # Markdown report + optional local LLM
examples/
  sample_report.md  # Sample output from a real scan
tests/
  test_agent.py     # pytest suite
```

## Technologies

- DataHub (open-source context platform)
- Python 3.9+
- FastAPI + Uvicorn
- Streamlit
- pytest
- Optional: Ollama-compatible local LLM for risk explanations

## License

Apache License 2.0 — see [LICENSE](LICENSE).
