"""DataHub REST/GraphQL client helpers for LineageGuard."""

import requests
import json
from typing import Dict, Any, Optional, List


class DataHubClient:
    def __init__(self, base_url: str = "http://localhost:8080", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["Content-Type"] = "application/json"

    def _graphql(self, query: str, variables: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/graphql"
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        r = self.session.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "errors" in data and data.get("data") is None:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        return data.get("data", {})

    def health(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def _normalize_entity(self, e: Dict[str, Any]) -> Dict[str, Any]:
        custom_props = {}
        for entry in e.get("properties", {}).get("customProperties", []) or []:
            val = entry.get("value", "")
            # If value looks like JSON array, parse it
            if val.startswith("[") and val.endswith("]"):
                try:
                    val = json.loads(val)
                except Exception:
                    pass
            custom_props[entry.get("key")] = val

        tags = []
        tag_data = e.get("tags", {})
        if tag_data and "tags" in tag_data:
            for t in tag_data["tags"]:
                tag_urn = t.get("tag", {}).get("urn", "")
                if tag_urn.startswith("urn:li:tag:"):
                    tags.append(tag_urn.replace("urn:li:tag:", ""))

        return {
            "urn": e["urn"],
            "type": e.get("type", "DATASET"),
            "name": e.get("name") or e["urn"].split(",")[-1].rstrip(")"),
            "platform": e.get("platform", {}).get("name", "unknown"),
            "properties": {
                "description": e.get("properties", {}).get("description", ""),
                "customProperties": custom_props,
                "tags": tags,
            },
        }

    def _fetch_entity(self, urn: str) -> Optional[Dict[str, Any]]:
        """Fetch a single dataset entity by URN."""
        query = """
        query getEntity($urn: String!) {
          dataset(urn: $urn) {
            urn
            type
            name
            platform { name }
            properties { name description customProperties { key value } }
            tags { tags { tag { urn } } }
          }
        }
        """
        try:
            data = self._graphql(query, {"urn": urn})
            entity = data.get("dataset")
            return self._normalize_entity(entity) if entity else None
        except Exception:
            return None

    def _fetch_neighbors(self, urn: str, direction: str) -> List[Dict[str, Any]]:
        """Fetch immediate lineage neighbors via searchAcrossLineage."""
        query = """
        query getNeighbors($urn: String!, $direction: LineageDirection!) {
          searchAcrossLineage(
            input: {
              urn: $urn
              direction: $direction
              count: 100
            }
          ) {
            searchResults {
              entity {
                urn
                type
                ... on Dataset {
                  name
                  platform { name }
                  properties { name description customProperties { key value } }
                  tags { tags { tag { urn } } }
                }
              }
            }
          }
        }
        """
        data = self._graphql(query, {"urn": urn, "direction": direction})
        results = []
        for r in data.get("searchAcrossLineage", {}).get("searchResults", []):
            entity = r.get("entity")
            if entity:
                results.append(self._normalize_entity(entity))
        return results

    def get_full_lineage(self, seed_urn: str, degrees: int = 3) -> Dict[str, Any]:
        """Build lineage graph by iterative expansion from seed."""
        nodes: Dict[str, Dict[str, Any]] = {}
        edge_map: Dict[tuple, Dict[str, Any]] = {}
        frontier = {seed_urn}
        visited = set()

        # Seed entity
        seed_entity = self._fetch_entity(seed_urn)
        if seed_entity:
            nodes[seed_urn] = seed_entity

        for _ in range(degrees):
            next_frontier = set()
            for urn in frontier:
                if urn in visited:
                    continue
                visited.add(urn)

                for direction in ("UPSTREAM", "DOWNSTREAM"):
                    try:
                        neighbors = self._fetch_neighbors(urn, direction)
                    except Exception:
                        continue
                    for neighbor in neighbors:
                        neighbor_urn = neighbor["urn"]
                        nodes[neighbor_urn] = neighbor
                        next_frontier.add(neighbor_urn)
                        if direction == "UPSTREAM":
                            edge_key = (neighbor_urn, urn)
                        else:
                            edge_key = (urn, neighbor_urn)
                        edge_map.setdefault(edge_key, {"source": edge_key[0], "target": edge_key[1], "type": direction})
            frontier = next_frontier
            if not frontier:
                break

        return {"entities": list(nodes.values()), "relationships": list(edge_map.values())}
