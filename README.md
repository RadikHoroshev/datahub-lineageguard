# LineageGuard: ML Supply Chain Security Agent for DataHub

An AI agent that protects ML pipelines by analyzing DataHub's end-to-end lineage graph.

## Problem

ML systems fail silently. Data poisoning, feature drift, shadow models, and unauthorized training data changes can break models in production before anyone notices. Existing tools monitor metrics, but they rarely trace the root cause back through the ML supply chain.

## Solution

LineageGuard uses DataHub's lineage graph to:
1. Map the ML pipeline: training data → features → model training → model deployment
2. Detect anomalies: tainted datasets, missing lineage, version mismatches, schema drift, shadow models
3. Write risk tags and assertions back into DataHub
4. Generate a security report with evidence and recommendations

## Quick Start

```bash
# 1. Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Start DataHub
datahub docker quickstart
# Open http://localhost:9002 (datahub / datahub)

# 3. Run synthetic demo
python -m lineageguard.agent
```

## Architecture

```
DataHub Graph (lineage)  --MCP/REST-->  LineageGuard Agent  --local LLM-->  Risk Report
                                            |
                                            v
                                    DataHub tags/assertions
```

## Hackathon Category

Category 3: **Build agents for ML teams that protect models in production** using DataHub's end-to-end ML lineage.

## License

Apache 2.0
