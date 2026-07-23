#!/usr/bin/env python3
"""
LineageGuard: ML Supply Chain Security Agent for DataHub

An agent that uses DataHub's end-to-end lineage to detect anomalies,
drift, and potential attacks in ML pipelines.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    DATA_DRIFT = "data_drift"
    FEATURE_DRIFT = "feature_drift"
    VERSION_MISMATCH = "version_mismatch"
    UNAUTHORIZED_SCHEMA_CHANGE = "unauthorized_schema_change"
    MISSING_LINEAGE = "missing_lineage"
    TAINTED_DATASET = "tainted_dataset"
    SHADOW_MODEL = "shadow_model"


@dataclass
class LineageNode:
    urn: str
    type: str
    name: str
    platform: str = "unknown"
    properties: Dict[str, Any] = field(default_factory=dict)


EMPTY_NODE = LineageNode("", "", "", "unknown")


@dataclass
class LineageEdge:
    source: str
    target: str
    relationship: str


@dataclass
class Anomaly:
    type: AnomalyType
    risk: RiskLevel
    description: str
    affected_urns: List[str]
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""


class LineageGuardAgent:
    """Core agent that analyzes ML lineage graph for security issues."""

    def __init__(self, datahub_client=None):
        self.client = datahub_client
        self.anomalies: List[Anomaly] = []

    def load_graph(self, lineage_json: Dict[str, Any]):
        """Load lineage graph from DataHub MCP/REST response."""
        self.nodes = {}
        self.edges = []
        for entity in lineage_json.get("entities", []):
            urn = entity.get("urn")
            self.nodes[urn] = LineageNode(
                urn=urn,
                type=entity.get("type"),
                name=entity.get("name", urn),
                platform=entity.get("platform", "unknown"),
                properties=entity.get("properties", {}),
            )
        for rel in lineage_json.get("relationships", []):
            self.edges.append(LineageEdge(
                source=rel.get("source"),
                target=rel.get("target"),
                relationship=rel.get("type"),
            ))
        logger.info(f"Loaded {len(self.nodes)} nodes, {len(self.edges)} edges")

    def detect_anomalies(self) -> List[Anomaly]:
        """Run all security checks."""
        self.anomalies = []
        self._check_missing_lineage()
        self._check_version_mismatch()
        self._check_tainted_datasets()
        self._check_shadow_models()
        return self.anomalies

    def _check_missing_lineage(self):
        """ML artifacts without upstream data lineage are suspicious."""
        for urn, node in self.nodes.items():
            if "mlModel" in node.type or "mlFeatureTable" in node.type:
                upstream = [e for e in self.edges if e.target == urn]
                if len(upstream) == 0 and node.platform != "unregistered":
                    self.anomalies.append(Anomaly(
                        type=AnomalyType.MISSING_LINEAGE,
                        risk=RiskLevel.HIGH,
                        description=f"{node.name} has no upstream lineage — cannot verify data provenance",
                        affected_urns=[urn],
                        recommendation="Document training data and feature sources in DataHub.",
                    ))

    def _check_version_mismatch(self):
        """Model version referenced in deployment differs from lineage/training."""
        model_versions = {}
        for urn, node in self.nodes.items():
            if "mlModel" in node.type:
                version = node.properties.get("customProperties", {}).get("version", "")
                if version:
                    model_versions[urn] = version

        for urn, node in self.nodes.items():
            if "endpoint" in node.name.lower() or "deployment" in node.name.lower():
                deployed_version = node.properties.get("customProperties", {}).get("model_version", "")
                # Find upstream model
                upstream_models = [
                    e.source for e in self.edges
                    if e.target == urn and "mlModel" in self.nodes.get(e.source, EMPTY_NODE).type
                ]
                for model_urn in upstream_models:
                    trained_version = model_versions.get(model_urn, "")
                    if trained_version and deployed_version and trained_version != deployed_version:
                        self.anomalies.append(Anomaly(
                            type=AnomalyType.VERSION_MISMATCH,
                            risk=RiskLevel.HIGH,
                            description=f"Model {self.nodes[model_urn].name} version {trained_version} deployed as {deployed_version}",
                            affected_urns=[model_urn, urn],
                            evidence={"trained_version": trained_version, "deployed_version": deployed_version},
                            recommendation="Align deployment with trained model version or rollback.",
                        ))

    def _get_tags(self, node):
        """Extract tags from node properties or customProperties."""
        props = node.properties or {}
        tags = []
        if isinstance(props.get("tags"), list):
            tags.extend(props["tags"])
        custom = props.get("customProperties", {})
        if isinstance(custom.get("tags"), list):
            tags.extend(custom["tags"])
        return [t.lower() for t in tags]

    def _check_tainted_datasets(self):
        """Detect datasets marked as tainted/poisoned."""
        for urn, node in self.nodes.items():
            tags = self._get_tags(node)
            if any(t in tags for t in ("tainted", "poisoned")):
                downstream = [e.target for e in self.edges if e.source == urn]
                self.anomalies.append(Anomaly(
                    type=AnomalyType.TAINTED_DATASET,
                    risk=RiskLevel.CRITICAL,
                    description=f"Tainted dataset {node.name} feeds {len(downstream)} downstream assets",
                    affected_urns=[urn] + downstream,
                    recommendation="Quarantine dataset and retrain downstream models.",
                ))

    def _check_shadow_models(self):
        """Models not registered in approved model registry."""
        for urn, node in self.nodes.items():
            if "mlModel" in node.type:
                tags = self._get_tags(node)
                platform = node.platform.lower()
                if "unregistered" in platform or "shadow" in tags:
                    self.anomalies.append(Anomaly(
                        type=AnomalyType.SHADOW_MODEL,
                        risk=RiskLevel.MEDIUM,
                        description=f"Model {node.name} appears unregistered or shadow",
                        affected_urns=[urn],
                        recommendation="Register model in approved model registry.",
                    ))

    def generate_report(self) -> Dict[str, Any]:
        """Generate JSON security report."""
        return {
            "summary": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "anomalies_count": len(self.anomalies),
                "critical": sum(1 for a in self.anomalies if a.risk == RiskLevel.CRITICAL),
                "high": sum(1 for a in self.anomalies if a.risk == RiskLevel.HIGH),
                "medium": sum(1 for a in self.anomalies if a.risk == RiskLevel.MEDIUM),
                "low": sum(1 for a in self.anomalies if a.risk == RiskLevel.LOW),
            },
            "anomalies": [
                {
                    "type": a.type.value,
                    "risk": a.risk.value,
                    "description": a.description,
                    "affected_urns": a.affected_urns,
                    "evidence": a.evidence,
                    "recommendation": a.recommendation,
                }
                for a in self.anomalies
            ],
        }


if __name__ == "__main__":
    # Demo with synthetic lineage
    demo_lineage = {
        "entities": [
            {"urn": "urn:li:dataset:(urn:li:dataPlatform:s3,training-data,PROD)",
             "type": "dataset", "name": "training-data", "platform": "s3",
             "properties": {"tags": ["tainted"]}},
            {"urn": "urn:li:dataset:(urn:li:dataPlatform:s3,features,PROD)",
             "type": "dataset", "name": "features", "platform": "s3",
             "properties": {}},
            {"urn": "urn:li:mlFeatureTable:(urn:li:dataPlatform:feast,feature-table,PROD)",
             "type": "mlFeatureTable", "name": "feature-table", "platform": "feast",
             "properties": {}},
            {"urn": "urn:li:mlModel:(urn:li:dataPlatform:mlflow,fraud-model,PROD)",
             "type": "mlModel", "name": "fraud-model", "platform": "mlflow",
             "properties": {}},
            {"urn": "urn:li:mlModel:(urn:li:dataPlatform:unregistered,shadow-model,PROD)",
             "type": "mlModel", "name": "shadow-model", "platform": "unregistered",
             "properties": {}},
        ],
        "relationships": [
            {"source": "urn:li:dataset:(urn:li:dataPlatform:s3,training-data,PROD)",
             "target": "urn:li:dataset:(urn:li:dataPlatform:s3,features,PROD)",
             "type": "DerivedFrom"},
            {"source": "urn:li:dataset:(urn:li:dataPlatform:s3,features,PROD)",
             "target": "urn:li:mlFeatureTable:(urn:li:dataPlatform:feast,feature-table,PROD)",
             "type": "Produces"},
            {"source": "urn:li:mlFeatureTable:(urn:li:dataPlatform:feast,feature-table,PROD)",
             "target": "urn:li:mlModel:(urn:li:dataPlatform:mlflow,fraud-model,PROD)",
             "type": "Trains"},
        ],
    }

    agent = LineageGuardAgent()
    agent.load_graph(demo_lineage)
    agent.detect_anomalies()
    report = agent.generate_report()
    print(json.dumps(report, indent=2))
