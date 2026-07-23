#!/usr/bin/env python3
"""CLI for LineageGuard."""

import json
import argparse
from pathlib import Path

from lineageguard.agent import LineageGuardAgent
from lineageguard.demo_data import build_demo_lineage


def main():
    parser = argparse.ArgumentParser(description="LineageGuard: ML Supply Chain Security Agent")
    parser.add_argument("--lineage", type=Path, help="Path to lineage JSON file")
    parser.add_argument("--output", type=Path, default=Path("lineageguard_report.json"), help="Report output path")
    parser.add_argument("--demo", action="store_true", help="Run on synthetic demo data")
    args = parser.parse_args()

    agent = LineageGuardAgent()

    if args.demo or not args.lineage:
        print("Running on synthetic demo lineage...")
        agent.load_graph(build_demo_lineage())
    else:
        print(f"Loading lineage from {args.lineage}...")
        agent.load_graph(json.loads(args.lineage.read_text()))

    agent.detect_anomalies()
    report = agent.generate_report()

    args.output.write_text(json.dumps(report, indent=2))
    print(f"Report saved to {args.output}")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
