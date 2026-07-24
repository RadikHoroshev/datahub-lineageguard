# Devpost — LineageGuard

**Project name:** LineageGuard  
**Tagline:** Catch poisoned data, shadow models, and version lies in your ML supply chain — powered by DataHub lineage.  
**Repo:** https://github.com/RadikHoroshev/datahub-lineageguard  
**Category:** AI agents for ML teams that protect models in production (DataHub ML lineage)

## Elevator pitch (≤280 chars)

LineageGuard is an ML supply-chain security agent that reads DataHub lineage, detects tainted datasets, shadow models, version mismatches, and missing lineage, then produces an actionable security report—with optional local LLM explanations.

## The problem

ML pipelines fail silently. Data poisoning, unregistered shadow models, and deployment version skew break production models before metrics look wrong. Observability rarely traces risk through the full training → feature → model → deploy graph.

## What we built

- **Anomaly agent** over DataHub lineage (GraphQL)
- Detectors: `version_mismatch`, `tainted_dataset`, `shadow_model`, `missing_lineage`
- **Synthetic pipeline ingest** for reproducible demos
- **CLI**, **FastAPI**, **Streamlit** UI
- **Markdown security reports** (+ optional local LLM explainer with graceful degradation)

## How it works

```
DataHub lineage graph
        │ GraphQL
        ▼
 LineageGuard agent ──► risk report (JSON/MD)
        │
        └── optional tags/assertions write-back (roadmap)
```

## Demo

1. DataHub: http://localhost:9002 (`datahub` / `datahub`)  
2. Streamlit: http://localhost:8501 → **Scan Lineage**  
3. CLI: `python -m lineageguard.run_real`  

Live scan finds three planted anomalies (critical tainted dataset, high version mismatch, medium shadow model).

## Tech stack

Python · DataHub · GraphQL · FastAPI · Streamlit · pytest · optional Ollama/local LLM

## What's next

- Write-back risk tags into DataHub  
- Schema/feature drift heuristics  
- CI + hosted demo URL  
- Hardened MCP integration  

## Built with

DataHub · acryl-datahub · FastAPI · Streamlit · Pydantic · pytest  

## Team

Radik Horoshev  

## Links

- GitHub: https://github.com/RadikHoroshev/datahub-lineageguard  
- DEMO.md (runbook): in repo root  
