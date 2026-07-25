#!/usr/bin/env python3
"""Fetch ML pipeline lineage from DataHub and run LineageGuard on it."""

import argparse
import json
import time
from pathlib import Path

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


def print_demo_report(report: dict, pause: float = 2.5) -> None:
    """Pretty-print anomalies one-by-one for demo video."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        console = Console()
    except ImportError:
        console = None

    summary = report.get("summary", {})
    anomalies = report.get("anomalies", [])

    def _plain():
        print("\n=== LineageGuard Scan Report ===")
        print(f"Nodes: {summary.get('total_nodes')} | Edges: {summary.get('total_edges')}")
        print(f"Anomalies: {summary.get('anomalies_count')} | Critical: {summary.get('critical')} | High: {summary.get('high')} | Medium: {summary.get('medium')}")
        for a in anomalies:
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(a.get("risk", "low"), "⚪")
            print(f"\n{emoji} [{a.get('risk').upper()}] {a.get('type')}")
            print(f"   {a.get('description')}")
            print(f"   Recommendation: {a.get('recommendation')}")
            time.sleep(pause)

    if console is None:
        _plain()
        return

    console.print()
    console.print(Panel.fit(
        f"[bold white]LineageGuard Scan Report[/bold white]\n"
        f"[green]Nodes:[/green] {summary.get('total_nodes')}  [green]Edges:[/green] {summary.get('total_edges')}  "
        f"[red]Anomalies:[/red] {summary.get('anomalies_count')}  "
        f"[red]Critical:[/red] {summary.get('critical')}  [yellow]High:[/yellow] {summary.get('high')}  [yellow]Medium:[/yellow] {summary.get('medium')}",
        title="LineageGuard", border_style="blue"
    ))

    for a in anomalies:
        risk = a.get("risk", "low")
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(risk, "⚪")
        risk_styles = {"critical": "red", "high": "orange3", "medium": "yellow", "low": "green"}
        title_text = f"{emoji} {risk.upper()}: {a.get('type')}"
        body = Text()
        body.append(a.get("description", ""), style="white")
        body.append("\n\nRecommendation: ", style="bold")
        body.append(a.get("recommendation", ""), style="green")
        console.print(Panel(body, title=title_text, border_style=risk_styles.get(risk, "white")))
        time.sleep(pause)


def main():
    parser = argparse.ArgumentParser(description="LineageGuard DataHub scanner")
    parser.add_argument("--demo-mode", action="store_true", help="Show anomalies one-by-one with pauses")
    parser.add_argument("--pause", type=float, default=2.5, help="Seconds between anomaly cards in demo mode")
    parser.add_argument("--json", action="store_true", help="Output full JSON report at the end")
    args = parser.parse_args()

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

    if args.demo_mode:
        print_demo_report(report, pause=args.pause)
    else:
        print(json.dumps(report, indent=2))

    if args.json and args.demo_mode:
        print("\n--- JSON Report ---")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
