"""Streamlit demo UI for LineageGuard."""

import json
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lineageguard.datahub_client import DataHubClient
from lineageguard.agent import LineageGuardAgent
from lineageguard.explainer import Explainer


st.set_page_config(page_title="LineageGuard", layout="wide")
st.title("LineageGuard: ML Supply Chain Security Agent for DataHub")

seed = st.text_input(
    "Seed URN",
    value="urn:li:dataset:(urn:li:dataPlatform:s3,fraud-features,PROD)",
)

if st.button("Scan Lineage"):
    with st.spinner("Fetching lineage from DataHub and detecting anomalies..."):
        client = DataHubClient("http://localhost:8080")
        try:
            lineage = client.get_full_lineage(seed, degrees=2)
            source = f"DataHub ({len(lineage['entities'])} nodes, {len(lineage['relationships'])} edges)"
        except Exception as e:
            st.error(f"DataHub fetch failed: {e}")
            from lineageguard.demo_data import build_demo_lineage
            lineage = build_demo_lineage()
            source = "synthetic demo data"

        agent = LineageGuardAgent(client)
        agent.load_graph(lineage)
        report = agent.generate_report()
        explainer = Explainer()

        st.success(f"Scan complete using {source}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nodes", report["summary"]["total_nodes"])
        col2.metric("Edges", report["summary"]["total_edges"])
        col3.metric("Anomalies", report["summary"]["anomalies_count"])
        col4.metric("Critical", report["summary"]["critical"])

        if report["anomalies"]:
            st.subheader("Detected Anomalies")
            for anomaly in report["anomalies"]:
                color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green"}.get(anomaly["risk"], "gray")
                with st.expander(f"{anomaly['risk'].upper()} — {anomaly['type']}", expanded=True):
                    st.markdown(f"**{anomaly['description']}**")
                    st.json(anomaly.get("evidence", {}))
                    st.markdown(f"*Recommendation:* {anomaly['recommendation']}")
                    st.markdown("Affected URNs:")
                    for urn in anomaly["affected_urns"]:
                        st.code(urn)

        with st.expander("Full Markdown Report"):
            st.markdown(explainer.explain(report))

        with st.expander("Raw JSON"):
            st.json(report)
