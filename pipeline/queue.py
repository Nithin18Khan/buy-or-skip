from __future__ import annotations

import json
from pathlib import Path

STATE = "factory_state.json"


def state_path(root: Path) -> Path:
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    return data / STATE


def load_state(root: Path) -> dict:
    path = state_path(root)
    if not path.exists():
        return {"rendered": {}, "uploaded": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(root: Path, state: dict) -> None:
    state_path(root).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def load_manifest(root: Path) -> dict:
    path = root / "scripts" / "calendar" / "90day.json"
    if not path.exists():
        raise FileNotFoundError("No 90-day calendar. Run: python main.py --plan-90")
    return json.loads(path.read_text(encoding="utf-8"))


def pending(root: Path, *, need: str = "render") -> list[dict]:
    man = load_manifest(root)
    st = load_state(root)
    done = st.get("uploaded" if need == "upload" else "rendered") or {}
    return [item for item in man.get("episodes") or [] if item["id"] not in done]
