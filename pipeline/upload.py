"""YouTube upload for the Money Tools adult channel only."""

from __future__ import annotations

import json
import os
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
CLIENT_SECRET = "client_secret.json"
TOKEN_FILE = "token.json"


def youtube_auth_available(root: Path) -> bool:
    if (root / "credentials" / CLIENT_SECRET).exists():
        return True
    if os.environ.get("YOUTUBE_CLIENT_SECRET_JSON", "").strip() and (
        os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
        or os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    ):
        return True
    return False


def _hydrate(root: Path) -> Path:
    creds = root / "credentials"
    creds.mkdir(parents=True, exist_ok=True)
    secret_json = os.environ.get("YOUTUBE_CLIENT_SECRET_JSON", "").strip()
    if secret_json:
        (creds / CLIENT_SECRET).write_text(secret_json, encoding="utf-8")
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    if token_json:
        (creds / TOKEN_FILE).write_text(token_json, encoding="utf-8")
    return creds


def _creds_from_refresh(creds_dir: Path):
    from google.oauth2.credentials import Credentials

    refresh = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
    secret = creds_dir / CLIENT_SECRET
    if not refresh or not secret.exists():
        return None
    blob = json.loads(secret.read_text(encoding="utf-8"))
    body = blob.get("installed") or blob.get("web") or blob
    return Credentials(
        token=None,
        refresh_token=refresh,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=body["client_id"],
        client_secret=body["client_secret"],
        scopes=SCOPES,
    )


def upload_video(episode: dict, video_path: Path, *, root: Path) -> dict:
    if episode.get("made_for_kids") is True:
        raise ValueError("Money Tools must never upload Made for Kids")
    if str(episode.get("language") or "en") != "en":
        raise ValueError("English only")
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    creds_dir = _hydrate(root)
    secret = creds_dir / CLIENT_SECRET
    if not secret.exists() and not youtube_auth_available(root):
        raise FileNotFoundError("Missing credentials. See credentials/HOW_TO_AUTH.txt")

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    token_path = creds_dir / TOKEN_FILE
    creds = _creds_from_refresh(creds_dir)
    if creds is None and token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds is None:
        raise RuntimeError("No YouTube refresh token. See credentials/HOW_TO_AUTH.txt")
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
    token_path.write_text(creds.to_json(), encoding="utf-8")

    youtube = build("youtube", "v3", credentials=creds)
    channel = json.loads((root / "config" / "channel.json").read_text(encoding="utf-8"))
    expected = str(channel.get("youtube_channel_id") or "").strip()
    if expected:
        mine = youtube.channels().list(part="id", mine=True).execute()
        items = mine.get("items") or []
        actual = str((items[0] or {}).get("id") or "") if items else ""
        if actual != expected:
            raise RuntimeError(
                f"Logged into {actual or '(none)'}, not Money Tools {expected}. "
                "Never use the kids or gaming channel."
            )
        print(f"YouTube: Money Tools channel {actual} OK")
    elif not expected:
        print("WARNING: config/channel.json has no youtube_channel_id yet.")

    disclosure = str(channel.get("disclosure") or "")
    desc = str(episode.get("description") or episode["title"])
    if disclosure.lower() not in desc.lower():
        desc = disclosure + "\n\n" + desc
    tracking = str((episode.get("affiliate") or {}).get("tracking_url") or "").strip()
    if tracking:
        desc += f"\n\nTool in this video:\n{tracking}"

    title = str(episode.get("youtube_title") or episode["title"])[:100]
    body = {
        "snippet": {
            "title": title,
            "description": desc[:4900],
            "tags": list(episode.get("tags") or ["tools", "review", "affiliate"]),
            "categoryId": str((channel.get("upload") or {}).get("category_id") or "28"),
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": (channel.get("upload") or {}).get("privacy_status") or "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"Uploading adult long-form → {video_path.name}")
    response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    video_id = response.get("id")
    url = f"https://youtu.be/{video_id}" if video_id else ""
    print(f"Uploaded: {url}")
    return {"id": video_id, "url": url, "title": title}
