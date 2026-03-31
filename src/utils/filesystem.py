from __future__ import annotations

import json
import csv
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


def processed_data_root() -> Path:
    path = ROOT_DIR / "data" / "processed"
    path.mkdir(parents=True, exist_ok=True)
    return path


def warehouse_data_root() -> Path:
    path = processed_data_root() / "warehouse"
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


def write_csv_records(records: list[dict[str, Any]], subdirectory: str, file_name: str) -> Path:
    target_dir = processed_data_root() / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file_name

    if not records:
        with target_path.open("w", encoding="utf-8", newline="") as file:
            file.write("")
        return target_path

    fieldnames = list(records[0].keys())
    with target_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    return target_path
