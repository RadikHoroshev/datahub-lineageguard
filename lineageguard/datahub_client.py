"""DataHub REST client helpers for LineageGuard."""

import requests
import json
from typing import Dict, Any, Optional


class DataHubClient:
    def __init__(self, base_url: str = "http://localhost:9002", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["Content-Type"] = "application/json"

    def health(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def get_lineage(self, urn: str, direction: str = "BOTH", degrees: int = 3) -> Dict[str, Any]:
        """Fetch lineage graph for a given URN."""
        body = {
            "urn": urn,
            "direction": direction,
            "degrees": degrees,
            "includeGhostEntities": False,
        }
        url = f"{self.base_url}/api/v2/graphql"
        query = """
        query getLineage($urn: String!, $direction: LineageDirection!, $degrees: Int!) {
          lineage(urn: $urn, direction: $direction, degrees: $degrees) {
            entities {
              urn
              type
              ... on Dataset {
                name
                platform { name }
                properties { name description customProperties }
              }
              ... on MLModel {
                name
                platform { name }
                properties { name description customProperties }
              }
              ... on MLFeatureTable {
                name
                platform { name }
                properties { name description customProperties }
              }
            }
            relationships { source target type }
          }
        }
        """
        payload = {"query": query, "variables": body}
        r = self.session.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        return data["data"]["lineage"]

    def emit_tags(self, urn: str, tags: list) -> bool:
        """Attach risk tags back to DataHub (simplified)."""
        # Real implementation would use DataHub REST emit endpoint
        return True
