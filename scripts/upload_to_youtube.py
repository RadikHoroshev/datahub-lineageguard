#!/usr/bin/env python3
"""Upload LineageGuard demo video to YouTube via OAuth.

Prerequisites:
1. Go to https://console.cloud.google.com/
2. Create/select a project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download client_secret.json and place it at scripts/client_secret.json
6. Run this script and authorize in the opened browser
7. Video will upload and the URL will be printed
"""

import os
import pickle
from pathlib import Path

from typing import List, Optional

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError as e:
    raise ImportError("Install google-api-python-client google-auth-httplib2 google-auth-oauthlib") from e


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = Path(__file__).with_name("client_secret.json")
TOKEN_FILE = Path(__file__).with_name("youtube_token.pickle")
VIDEO_FILE = Path(__file__).resolve().parent.parent / "demo_video" / "demo_final.mp4"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Place Google Cloud OAuth Desktop credentials at {CREDENTIALS_FILE}\n"
                    "Get them at https://console.cloud.google.com/ under APIs & Services > Credentials"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds


def upload_video(
    title: str = "LineageGuard: ML Supply Chain Security Agent for DataHub",
    description: str = (
        "LineageGuard protects ML models in production by analyzing DataHub's "
        "end-to-end lineage graph. Built for the Build with DataHub: The Agent Hackathon.\n\n"
        "GitHub: https://github.com/RadikHoroshev/datahub-lineageguard\n"
        "Devpost: https://devpost.com/software/lineageguard-tmvhr4"
    ),
    tags: Optional[List[str]] = None,
    privacy_status: str = "unlisted",
) -> str:
    if not VIDEO_FILE.exists():
        raise FileNotFoundError(f"Video not found: {VIDEO_FILE}")

    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["DataHub", "ML", "lineage", "security", "AI agent", "hackathon"],
            "categoryId": "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(VIDEO_FILE), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part=", ".join(body.keys()), body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Upload complete: {url}")
    return url


if __name__ == "__main__":
    upload_video()
