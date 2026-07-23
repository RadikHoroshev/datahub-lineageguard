"""Synthetic ML pipeline generator for DataHub demos."""

import json
from pathlib import Path
from typing import Dict, Any, List


def build_demo_lineage() -> Dict[str, Any]:
    """Return a synthetic ML pipeline lineage graph with planted anomalies."""
    return {
        "entities": [
            {
                "urn": "urn:li:dataset:(urn:li:dataPlatform:s3,customer-transactions,PROD)",
                "type": "dataset",
                "name": "customer-transactions",
                "platform": "s3",
                "properties": {
                    "description": "Raw customer transactions",
                    "customProperties": {"owner": "data-platform", "pii": "true"},
                },
            },
            {
                "urn": "urn:li:dataset:(urn:li:dataPlatform:s3,transactions-v2-poisoned,PROD)",
                "type": "dataset",
                "name": "transactions-v2-poisoned",
                "platform": "s3",
                "properties": {
                    "description": "Updated transaction feed",
                    "customProperties": {"tags": ["tainted"]},
                },
            },
            {
                "urn": "urn:li:dataset:(urn:li:dataPlatform:s3,fraud-features,PROD)",
                "type": "dataset",
                "name": "fraud-features",
                "platform": "s3",
                "properties": {"description": "Engineered features for fraud model"},
            },
            {
                "urn": "urn:li:mlFeatureTable:(urn:li:dataPlatform:feast,fraud-feature-table,PROD)",
                "type": "mlFeatureTable",
                "name": "fraud-feature-table",
                "platform": "feast",
                "properties": {"description": "Online feature table"},
            },
            {
                "urn": "urn:li:mlModel:(urn:li:dataPlatform:mlflow,fraud-detection-model,PROD)",
                "type": "mlModel",
                "name": "fraud-detection-model",
                "platform": "mlflow",
                "properties": {
                    "description": "Production fraud detection model",
                    "customProperties": {"version": "v1.2.3"},
                },
            },
            {
                "urn": "urn:li:mlModel:(urn:li:dataPlatform:unregistered,shadow-fraud-model,PROD)",
                "type": "mlModel",
                "name": "shadow-fraud-model",
                "platform": "unregistered",
                "properties": {"description": "Unregistered shadow model"},
            },
            {
                "urn": "urn:li:dataset:(urn:li:dataPlatform:sagemaker,fraud-model-endpoint,PROD)",
                "type": "dataset",
                "name": "fraud-model-endpoint",
                "platform": "sagemaker",
                "properties": {
                    "description": "Deployed model endpoint",
                    "customProperties": {"model_version": "v1.2.1"},
                },
            },
        ],
        "relationships": [
            {
                "source": "urn:li:dataset:(urn:li:dataPlatform:s3,customer-transactions,PROD)",
                "target": "urn:li:dataset:(urn:li:dataPlatform:s3,fraud-features,PROD)",
                "type": "DerivedFrom",
            },
            {
                "source": "urn:li:dataset:(urn:li:dataPlatform:s3,transactions-v2-poisoned,PROD)",
                "target": "urn:li:dataset:(urn:li:dataPlatform:s3,fraud-features,PROD)",
                "type": "DerivedFrom",
            },
            {
                "source": "urn:li:dataset:(urn:li:dataPlatform:s3,fraud-features,PROD)",
                "target": "urn:li:mlFeatureTable:(urn:li:dataPlatform:feast,fraud-feature-table,PROD)",
                "type": "Produces",
            },
            {
                "source": "urn:li:mlFeatureTable:(urn:li:dataPlatform:feast,fraud-feature-table,PROD)",
                "target": "urn:li:mlModel:(urn:li:dataPlatform:mlflow,fraud-detection-model,PROD)",
                "type": "Trains",
            },
            {
                "source": "urn:li:mlModel:(urn:li:dataPlatform:mlflow,fraud-detection-model,PROD)",
                "target": "urn:li:dataset:(urn:li:dataPlatform:sagemaker,fraud-model-endpoint,PROD)",
                "type": "Serves",
            },
        ],
    }


def save_demo_lineage(path: Path = Path("examples/demo_lineage.json")) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_demo_lineage(), indent=2))
    return path


if __name__ == "__main__":
    p = save_demo_lineage()
    print(f"Saved demo lineage to {p}")
