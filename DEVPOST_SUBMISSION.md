# Devpost Submission — LineageGuard

Ready-to-paste fields for https://datahub.devpost.com submission form.

## Project name

LineageGuard

## Tagline (≤140 chars)

Catch poisoned data, shadow models, and version lies in your ML supply chain — powered by DataHub lineage.

## Elevator pitch (≤280 chars)

LineageGuard is an ML supply-chain security agent that reads DataHub's end-to-end ML lineage, detects tainted datasets, shadow models, version mismatches, and missing lineage, then generates actionable security reports — with optional local LLM explanations.

## About this project

ML pipelines fail silently. A poisoned training dataset, an unregistered shadow model, or a deployment running the wrong model version can break production systems weeks before dashboards show drift. Existing tools monitor metrics; LineageGuard monitors the *graph*.

We built LineageGuard for the **Build with DataHub: The Agent Hackathon** Challenge 3 — agents that protect ML models in production. It reads upstream/downstream lineage from DataHub via GraphQL, walks the path from raw datasets → features → feature tables → models → deployment endpoints, and flags four concrete anomaly classes:

- **Tainted datasets** — upstream assets tagged `tainted`/`poisoned` that feed production features or models
- **Version mismatch** — deployed endpoint model version differs from the trained model version in lineage
- **Shadow models** — unregistered or untracked models connected to production assets
- **Missing lineage** — production models or feature tables with no provenance

The agent outputs a structured JSON report, a human-readable Markdown explanation, and an optional LLM-generated risk narrative. It ships with a synthetic fraud-detection ML pipeline ingested into DataHub, plus a CLI, FastAPI server, and Streamlit UI for live demos.

A real scan against the seeded DataHub instance surfaces three planted issues: a **critical** tainted dataset feeding five downstream assets, a **high** version mismatch (v1.2.3 trained model deployed as v1.2.1), and a **medium** unregistered shadow model.

## Built With

- DataHub (open-source metadata & context platform)
- acryl-datahub (Python SDK / CLI)
- Python
- GraphQL
- FastAPI
- Streamlit
- Pydantic
- pytest
- Optional: Ollama-compatible local LLM for risk explanations

## Try it out

1. Start DataHub locally:
   ```bash
   pip install acryl-datahub
   datahub docker quickstart
   ```
   Open http://localhost:9002 and log in with `datahub` / `datahub`.

2. Clone and install:
   ```bash
   git clone https://github.com/RadikHoroshev/datahub-lineageguard.git
   cd datahub-lineageguard
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Seed the demo ML pipeline:
   ```bash
   python -m lineageguard.ingest
   ```

4. Run a security scan:
   ```bash
   python -m lineageguard.run_real
   ```

5. Launch the Streamlit demo:
   ```bash
   streamlit run lineageguard/app.py
   ```
   Open http://localhost:8501 and click **Scan Lineage**.

## Public repository

https://github.com/RadikHoroshev/datahub-lineageguard

## Demo video

TODO — upload to YouTube/Vimeo and paste URL here.

## Submission checklist

- [x] Public GitHub repo with Apache 2.0 license
- [x] Working code + tests
- [x] Setup instructions in README
- [x] Demo runbook (DEMO.md) and sample output (examples/)
- [ ] 3-minute demo video uploaded
- [ ] Devpost submission fields filled and submitted
