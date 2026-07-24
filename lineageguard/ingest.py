#!/usr/bin/env python3
"""Ingest synthetic ML pipeline lineage into DataHub using datasets."""

import json
from pathlib import Path

from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    GlobalTagsClass,
    TagAssociationClass,
    UpstreamLineageClass,
    UpstreamClass,
)


def tag(name: str) -> TagAssociationClass:
    return TagAssociationClass(tag=f"urn:li:tag:{name}")


def ingest_ml_pipeline(emitter: DatahubRestEmitter):
    nodes = {
        "customer-transactions": {
            "platform": "s3",
            "props": DatasetPropertiesClass(
                name="customer-transactions",
                description="Raw customer transactions",
                customProperties={"owner": "data-platform", "pii": "true"},
            ),
            "tags": None,
        },
        "transactions-v2-poisoned": {
            "platform": "s3",
            "props": DatasetPropertiesClass(
                name="transactions-v2-poisoned",
                description="Updated transaction feed",
                customProperties={"tags": json.dumps(["tainted"])},
            ),
            "tags": ["tainted"],
        },
        "fraud-features": {
            "platform": "s3",
            "props": DatasetPropertiesClass(
                name="fraud-features",
                description="Engineered features for fraud model",
            ),
            "tags": None,
        },
        "fraud-feature-table": {
            "platform": "feast",
            "props": DatasetPropertiesClass(
                name="fraud-feature-table",
                description="Online feature table (Feast)",
            ),
            "tags": None,
        },
        "fraud-detection-model": {
            "platform": "mlflow",
            "props": DatasetPropertiesClass(
                name="fraud-detection-model",
                description="Production fraud detection model",
                customProperties={"version": "v1.2.3", "type": "mlmodel"},
            ),
            "tags": None,
        },
        "shadow-fraud-model": {
            "platform": "unregistered",
            "props": DatasetPropertiesClass(
                name="shadow-fraud-model",
                description="Unregistered shadow model",
                customProperties={"type": "mlmodel"},
            ),
            "tags": ["shadow"],
        },
        "fraud-model-endpoint": {
            "platform": "sagemaker",
            "props": DatasetPropertiesClass(
                name="fraud-model-endpoint",
                description="Deployed model endpoint",
                customProperties={"model_version": "v1.2.1", "type": "endpoint"},
            ),
            "tags": None,
        },
    }

    urns = {}
    for name, cfg in nodes.items():
        urn = make_dataset_urn(cfg["platform"], name)
        urns[name] = urn
        emitter.emit_mcp(MetadataChangeProposalWrapper(
            entityUrn=urn,
            aspect=cfg["props"],
        ))
        if cfg["tags"]:
            emitter.emit_mcp(MetadataChangeProposalWrapper(
                entityUrn=urn,
                aspect=GlobalTagsClass(tags=[tag(t) for t in cfg["tags"]]),
            ))
        print(f"Ingested dataset: {name}")

    # Lineage edges (dataset to dataset only for UpstreamLineageClass compatibility)
    edges = [
        ("fraud-features", ["customer-transactions", "transactions-v2-poisoned"], "TRANSFORMED"),
        ("fraud-feature-table", ["fraud-features"], "TRANSFORMED"),
        ("fraud-detection-model", ["fraud-feature-table"], "TRANSFORMED"),
        ("shadow-fraud-model", ["fraud-feature-table"], "TRANSFORMED"),
        ("fraud-model-endpoint", ["fraud-detection-model"], "TRANSFORMED"),
    ]

    for target_name, source_names, rel_type in edges:
        upstreams = [UpstreamClass(dataset=urns[s], type=rel_type) for s in source_names]
        emitter.emit_mcp(MetadataChangeProposalWrapper(
            entityUrn=urns[target_name],
            aspect=UpstreamLineageClass(upstreams=upstreams),
        ))
        print(f"Ingested lineage for: {target_name}")


def main():
    emitter = DatahubRestEmitter("http://localhost:8080")
    print(f"Connected to DataHub: {emitter.test_connection()}")
    ingest_ml_pipeline(emitter)
    print("ML pipeline ingestion complete.")


if __name__ == "__main__":
    main()
