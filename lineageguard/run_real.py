#!/usr/bin/env python3
"""Fetch ML pipeline lineage from DataHub and run LineageGuard on it."""

import json
from lineageguard.datahub_client import DataHubClient
from lineageguard.agent import LineageGuardAgent
from lineageguard.demo_data import build_demo_lineage


def lineage_to_agent_format(datahub_lineage: dict) -> dict:
    """Convert DataHub GraphQL lineage response into internal agent format."""
    entities = []
    for e in datahub_lineage.get("entities", []):
        entities.append({
            "urn": e.get("urn"),
            "type": e.get("type", "dataset"),
            "name": e.get("name") or e.get("urn").split(",")[-1].rstrip(")"),
            "platform": e.get("platform", {}).get("name", "unknown"),
            "properties": {
                "description": e.get("properties", {}).get("description", ""),
                "customProperties": e.get("properties", {}).get("customProperties", {}),
            },
        })

    relationships = []
    for r in datahub_lineage.get("relationships", []):
        relationships.append({
            "source": r.get("source"),
            "target": r.get("target"),
            "type": r.get("type", "UNKNOWN"),
        })

    return {"entities": entities, "relationships": relationships}


def main():
    # GMS REST endpoint does not require auth in quickstart mode
    client = DataHubClient("http://localhost:8080")
    print(f"DataHub health: {client.health()}")

    # Use synthetic data if DataHub lineage fetch fails
    try:
        lineage = client.get_full_lineage(
            "urn:li:dataset:(urn:li:dataPlatform:s3,fraud-features,PROD)",
            degrees=2,
        )
        print(f"Fetched {len(lineage['entities'])} nodes, {len(lineage['relationships'])} edges from DataHub")
    except Exception as e:
        print(f"DataHub fetch failed ({e}), using synthetic demo data.")
        lineage = build_demo_lineage()

    agent = LineageGuardAgent(client)
    agent.load_graph(lineage)
    agent.detect_anomalies()
    report = agent.generate_report()

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
