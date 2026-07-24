"""Autonomous Devpost submission for LineageGuard.

Reads submission answers from DEVPOST_SUBMISSION.md and submits the project
via Devpost MCP.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lineageguard.devpost_mcp import DevpostMCPClient


REPO_URL = "https://github.com/RadikHoroshev/datahub-lineageguard"
VIDEO_URL_PLACEHOLDER = "TODO_PASTE_VIDEO_URL"

SUBMISSION = {
    # Project-level fields (used by create_project + update_project)
    "name": "LineageGuard",
    "tagline": "Catch poisoned data, shadow models, and version lies in your ML supply chain — powered by DataHub lineage.",
    "description": """LineageGuard is an ML supply-chain security agent built for the DataHub Agent Hackathon's **Production ML Agents** challenge.

It reads DataHub's end-to-end ML lineage — training datasets → features → feature tables → models → deployment endpoints — and detects silent risks that break production ML systems:

- **Tainted datasets** — upstream assets tagged `tainted`/`poisoned` that feed production features or models
- **Version mismatch** — deployed endpoint model version differs from the trained model version in lineage
- **Shadow models** — unregistered or untracked models connected to production assets
- **Missing lineage** — production models or feature tables with no provenance

A live scan against the seeded DataHub quickstart surfaces three planted issues: a **critical** tainted dataset, a **high** version mismatch (v1.2.3 trained model deployed as v1.2.1), and a **medium** unregistered shadow model. The agent outputs a structured JSON report, a Markdown explanation, and an optional local-LLM risk narrative.

The repository includes a CLI, FastAPI server, Streamlit UI, synthetic ML pipeline ingestion script, and pytest suite.
""",
    "built_with": [
        "DataHub OSS / Core Platform",
        "acryl-datahub",
        "Python",
        "GraphQL",
        "FastAPI",
        "Streamlit",
        "Pydantic",
        "pytest",
    ],
    "repo_url": REPO_URL,
    "demo_url": REPO_URL,
    "video_url": VIDEO_URL_PLACEHOLDER,
}

SUBMISSION_FIELDS = [
    {"submission_field_id": 27765, "value": "Production ML Agents"},
    {"submission_field_id": 27838, "value": REPO_URL},
    {"submission_field_id": 27837, "value": REPO_URL},
    {"submission_field_id": 27839, "value": f"{REPO_URL}/tree/main/examples"},
    {"submission_field_id": 27767, "value": ["DataHub OSS / Core Platform", "DataHub MCP Server"]},
    {"submission_field_id": 27768, "value": ""},
    {"submission_field_id": 27840, "value": "Israel"},
    {"submission_field_id": 27841, "value": "Yes, newly created during the Submission Period"},
    {"submission_field_id": 27842, "value": ""},
    {"submission_field_id": 27843, "value": "Yes, consider me for the Feedback Prize"},
    {"submission_field_id": 27844, "value": "The GraphQL lineage API (`searchAcrossLineage`) was the most useful part of the build: it let the agent walk upstream/downstream from any seed dataset without needing to know the schema ahead of time. The `acryl-datahub` Python SDK made seeding the synthetic ML pipeline straightforward, and the DataHub UI gave immediate visual confirmation that the lineage graph was built correctly."},
    {"submission_field_id": 27845, "value": "The biggest time sink was getting `datahub docker quickstart` to run on macOS with limited local disk. The default Colima profile used the system disk and ran out of space; moving Colima to an external SSD and setting `DATAHUB_TOKEN_SERVICE_SIGNING_KEY` / `DATAHUB_TOKEN_SERVICE_SALT` before quickstart resolved it. The `UpstreamLineageClass` schema also required reading the Avro record to find the correct enum values for synthetic pipeline ingestion."},
    {"submission_field_id": 27846, "value": "First-class, bidirectional lineage for ML assets (not just datasets) — e.g., native MLModel and MLFeatureTable lineage edges — so agents don't have to model models as datasets. Second, a built-in policy/assertion framework for tagging risky assets automatically from agent findings."},
    {"submission_field_id": 27847, "value": "No blockers. The DataHub GraphQL endpoint returned correct lineage results once the right query shape was discovered by introspecting the schema."},
]


def main(video_url: str = VIDEO_URL_PLACEHOLDER, project_id: str = ""):
    client = DevpostMCPClient()

    # Create project if no project_id given
    if not project_id:
        project_payload = {
            "name": SUBMISSION["name"],
            "tagline": SUBMISSION["tagline"],
            "description": SUBMISSION["description"],
            "built_with": ", ".join(SUBMISSION["built_with"]),
            "links": [SUBMISSION["repo_url"], f"{SUBMISSION['repo_url']}/tree/main/examples"],
        }
        print("Creating project...")
        created = client.create_project(project_payload)
        print("Created project:", created)
        project_id = created["structuredContent"]["project_id"]

    # Update project with full content
    print("Updating project...")
    client.update_project(str(project_id), {
        "name": SUBMISSION["name"],
        "tagline": SUBMISSION["tagline"],
        "description": SUBMISSION["description"],
        "built_with": ", ".join(SUBMISSION["built_with"]),
        "links": [SUBMISSION["repo_url"], f"{SUBMISSION['repo_url']}/tree/main/examples"],
        "video_url": video_url,
    })

    # Submit to DataHub hackathon
    print("Submitting to DataHub hackathon...")
    submitted = client.submit_project(
        project_id=str(project_id),
        hackathon="datahub",
        submission={"custom_answers": SUBMISSION_FIELDS},
        video_url=video_url,
    )
    print("Submitted:", submitted)


if __name__ == "__main__":
    video_url = sys.argv[1] if len(sys.argv) > 1 else VIDEO_URL_PLACEHOLDER
    project_id = sys.argv[2] if len(sys.argv) > 2 else ""
    main(video_url, project_id)
