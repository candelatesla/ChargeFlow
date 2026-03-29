from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.config import ROOT_DIR, load_base_config


def raw_data_root() -> Path:
    config = load_base_config()
    raw_root = config["project"]["raw_data_root"]
    path = ROOT_DIR / raw_root
    path.mkdir(parents=True, exist_ok=True)
    return path


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_json(payload: dict[str, Any], source_name: str, file_stem: str) -> Path:
    target_dir = raw_data_root() / source_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{file_stem}_{timestamp_slug()}.json"
    with target_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
    return target_path
