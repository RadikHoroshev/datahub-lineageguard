# LineageGuard

**ML supply chain security agent for [DataHub](https://datahubproject.io/)**

Catch poisoned training data, shadow models, and deployment version lies — by walking the real lineage graph.

[![CI](https://github.com/RadikHoroshev/datahub-lineageguard/actions/workflows/ci.yml/badge.svg)](https://github.com/RadikHoroshev/datahub-lineageguard/actions/workflows/ci.yml)
[License](LICENSE) · [DEMO](DEMO.md) · [Devpost draft](DEVPOST.md) · [Roadmap](ROADMAP.md)

---

## Problem

ML systems fail **silently**. Data poisoning, feature contamination, unregistered shadow models, and train/serve version skew can break production before dashboards alarm. Metric monitors rarely answer: *which upstream asset poisoned this model?*

## Solution

LineageGuard is an agent that:

1. **Reads** end-to-end ML lineage from DataHub (GraphQL)
2. **Detects** supply-chain anomalies:
   - `version_mismatch` — trained vs deployed model versions diverge  
   - `tainted_dataset` — poisoned data reaches downstream models  
   - `shadow_model` — unregistered model outside the graph  
   - `missing_lineage` — gaps in the chain of custody  
3. **Reports** structured JSON + Markdown security findings  
4. **Explains** (optional) via local LLM with graceful degradation if Ollama is down  

## Architecture

```text
┌─────────────────┐     GraphQL      ┌──────────────────┐
│  DataHub GMS    │ ───────────────► │ LineageGuard     │
│  :8080 / UI:9002│                  │  agent.py        │
└─────────────────┘                  │  detectors       │
                                     └────────┬─────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
              CLI report                 FastAPI :8000            Streamlit :8501
           + Markdown MD                 /scan /health              Scan Lineage UI
```

## Quick start

```bash
git clone https://github.com/RadikHoroshev/datahub-lineageguard.git
cd datahub-lineageguard
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Unit tests (no DataHub required)
pytest tests/test_agent.py -q

# Synthetic demo (offline)
python -m lineageguard.cli --demo

# Full stack (local)
# 1) datahub docker quickstart  → http://localhost:9002  (datahub/datahub)
# 2) python -m lineageguard.ingest
# 3) python -m lineageguard.run_real
# 4) streamlit run lineageguard/app.py   → http://localhost:8501
```

## Demo (live machine)

| Surface | URL |
|--|--|
| DataHub UI | http://localhost:9002 |
| Streamlit | http://localhost:8501 |
| FastAPI | `uvicorn lineageguard.api:app --port 8000` |

See **[DEMO.md](DEMO.md)** for the 3-minute script and expected anomalies.

## Project layout

```text
lineageguard/
  agent.py           # anomaly detection engine
  datahub_client.py  # GraphQL lineage client
  ingest.py          # load synthetic ML pipeline into DataHub
  run_real.py        # end-to-end scan of live DataHub
  api.py             # FastAPI
  app.py             # Streamlit UI
  cli.py             # CLI
  explainer.py       # Markdown report + optional local LLM
  demo_data.py       # synthetic graph for tests
tests/test_agent.py
examples/demo_lineage.json
```

## Hackathon category

**Build agents for ML teams that protect models in production** using DataHub's end-to-end ML lineage.

## License

Apache 2.0 — see [LICENSE](LICENSE).
