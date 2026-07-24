"""Devpost MCP client wrapper for autonomous submission."""

import subprocess
import requests
from typing import Dict, Any, Optional


class DevpostMCPClient:
    """Call Devpost MCP tools using a Bearer token stored in macOS Keychain."""

    MCP_URL = "https://devpost.com/mcp"
    TOKEN_SERVICE = "devpost-mcp-token"

    def __init__(self, token: Optional[str] = None):
        self.token = token or self._read_token_from_keychain()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })
        self._id = 0

    @staticmethod
    def _read_token_from_keychain() -> str:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", DevpostMCPClient.TOKEN_SERVICE, "-w"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()

    def _call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }
        r = self.session.post(self.MCP_URL, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"Devpost MCP error: {data['error']}")
        return data["result"]

    def whoami(self) -> Dict[str, Any]:
        return self._call_tool("whoami")

    def list_hackathons(self) -> Dict[str, Any]:
        return self._call_tool("list_hackathons")

    def get_hackathon_overview(self, hackathon: str) -> Dict[str, Any]:
        return self._call_tool("get_hackathon_overview", {"hackathon": hackathon})

    def get_submission_requirements(self, hackathon: str) -> Dict[str, Any]:
        return self._call_tool("get_submission_requirements", {"hackathon": hackathon})

    def get_registration_form(self, hackathon: str) -> Dict[str, Any]:
        return self._call_tool("get_registration_form", {"hackathon": hackathon})

    def register_for_hackathon(self, hackathon: str, form: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._call_tool("register_for_hackathon", {"hackathon": hackathon, "form": form or {}})

    def create_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_tool("create_project", {"project": project})

    def update_project(self, project_id: str, project: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_tool("update_project", {"project": project_id, **project})

    def submit_project(self, project_id: str, hackathon: str, submission: Optional[Dict[str, Any]] = None, video_url: str = "") -> Dict[str, Any]:
        args = {
            "project": project_id,
            "challenge_slug": hackathon,
        }
        if video_url:
            args["video_url"] = video_url
        if submission:
            args.update(submission)
        return self._call_tool("submit_project", args)


if __name__ == "__main__":
    client = DevpostMCPClient()
    print(client.whoami())
    print(client.list_hackathons())
