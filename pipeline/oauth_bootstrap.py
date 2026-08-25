"""One-time OAuth for Money Tools. Never use kids or gaming JSON."""

from __future__ import annotations

import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = Path(__file__).resolve().parents[1]
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def main() -> None:
    secret = ROOT / "credentials" / "client_secret.json"
    if not secret.exists():
        raise SystemExit("Put this channel's OAuth JSON at credentials/client_secret.json")
    flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
    creds = flow.run_local_server(port=0)
    (ROOT / "credentials" / "token.json").write_text(creds.to_json(), encoding="utf-8")
    data = json.loads(creds.to_json())
    print("refresh_token:")
    print(data.get("refresh_token") or "(none — re-run and tick consent)")
    print("Add it to THIS repo's GitHub secrets only.")


if __name__ == "__main__":
    main()
