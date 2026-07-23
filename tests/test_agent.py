"""Tests for LineageGuard agent."""

import json
from lineageguard.agent import LineageGuardAgent, AnomalyType, RiskLevel
from lineageguard.demo_data import build_demo_lineage


def test_demo_anomalies():
    agent = LineageGuardAgent()
    agent.load_graph(build_demo_lineage())
    anomalies = agent.detect_anomalies()
    report = agent.generate_report()

    assert report["summary"]["total_nodes"] == 7
    assert report["summary"]["total_edges"] == 5
    assert report["summary"]["anomalies_count"] >= 3

    types = {a.type for a in anomalies}
    assert AnomalyType.TAINTED_DATASET in types
    assert AnomalyType.SHADOW_MODEL in types
    assert AnomalyType.VERSION_MISMATCH in types or AnomalyType.MISSING_LINEAGE in types

    # Check critical anomaly for tainted data
    critical = [a for a in anomalies if a.risk == RiskLevel.CRITICAL]
    assert len(critical) >= 1
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    test_demo_anomalies()
    print("All tests passed.")
