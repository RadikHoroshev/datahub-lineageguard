"""Local LLM explanations for anomalies."""

import json
from typing import Dict, Any, List, Optional

import requests


class Explainer:
    """Generate human-readable security explanations for detected anomalies.

    Rule-based by default; optionally calls a local Ollama LLM for richer prose.
    """

    def __init__(self, ollama_url: Optional[str] = "http://localhost:11434", model: str = "qwen3.5:9b"):
        self.ollama_url = ollama_url
        self.model = model

    def _call_llm(self, prompt: str) -> str:
        if not self.ollama_url:
            return ""
        try:
            r = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}},
                timeout=30,
            )
            r.raise_for_status()
            return r.json().get("response", "").strip()
        except Exception:
            # Graceful degradation: do not block report when LLM is slow/unavailable
            return ""

    def explain(self, report: Dict[str, Any]) -> str:
        lines = [
            f"# LineageGuard Security Report",
            f"",
            f"**Nodes scanned:** {report['summary']['total_nodes']}",
            f"**Edges scanned:** {report['summary']['total_edges']}",
            f"**Anomalies found:** {report['summary']['anomalies_count']}",
            f"**Risk breakdown:** 🚨 {report['summary']['critical']} critical, ⚠️ {report['summary']['high']} high, 🔶 {report['summary']['medium']} medium",
            f"",
        ]

        for i, anomaly in enumerate(report["anomalies"], 1):
            lines.append(f"## {i}. {anomaly['risk'].upper()} — {anomaly['type']}")
            lines.append(f"{anomaly['description']}")
            if anomaly.get("evidence"):
                lines.append(f"**Evidence:** `{json.dumps(anomaly['evidence'])}`")
            lines.append(f"**Recommendation:** {anomaly['recommendation']}")
            lines.append(f"**Affected assets:**")
            for urn in anomaly["affected_urns"]:
                lines.append(f"- `{urn}`")
            llm_prompt = self._build_llm_prompt(anomaly)
            llm_explanation = self._call_llm(llm_prompt)
            if llm_explanation:
                lines.append(f"**AI explanation:** {llm_explanation}")
            lines.append("")

        if not report["anomalies"]:
            lines.append("No supply-chain anomalies detected in the current lineage graph.")

        return "\n".join(lines)

    def explain_one(self, anomaly: Dict[str, Any]) -> str:
        report = {"summary": {"total_nodes": 0, "total_edges": 0, "anomalies_count": 1, "critical": 0, "high": 0, "medium": 0, "low": 0}, "anomalies": [anomaly]}
        return self.explain(report)

    def _build_llm_prompt(self, anomaly: Dict[str, Any]) -> str:
        return (
            "You are a machine-learning security analyst. Explain in 2 sentences why the following "
            "DataHub lineage anomaly is dangerous and what should be done first. Be specific.\n\n"
            f"Anomaly type: {anomaly['type']}\n"
            f"Risk level: {anomaly['risk']}\n"
            f"Description: {anomaly['description']}\n"
            f"Evidence: {json.dumps(anomaly.get('evidence', {}))}\n"
            f"Recommendation: {anomaly['recommendation']}\n"
        )
