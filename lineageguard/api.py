"""FastAPI server exposing LineageGuard agent."""

import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from lineageguard.agent import LineageGuardAgent
from lineageguard.demo_data import build_demo_lineage

app = FastAPI(title="LineageGuard", version="0.1.0")


class LineageInput(BaseModel):
    lineage: dict


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h1>LineageGuard: ML Supply Chain Security Agent</h1>
    <p>Endpoints:
    <ul>
      <li><a href="/docs">API docs</a></li>
      <li><code>POST /analyze/demo</code> — analyze synthetic demo lineage</li>
      <li><code>POST /analyze</code> — analyze custom lineage JSON</li>
    </ul>
    </p>
    """


@app.post("/analyze/demo")
def analyze_demo():
    agent = LineageGuardAgent()
    agent.load_graph(build_demo_lineage())
    agent.detect_anomalies()
    return agent.generate_report()


@app.post("/analyze")
def analyze(input: LineageInput):
    agent = LineageGuardAgent()
    agent.load_graph(input.lineage)
    agent.detect_anomalies()
    return agent.generate_report()
