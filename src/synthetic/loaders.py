from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.filesystem import raw_data_root


def load_latest_station_records() -> list[dict[str, Any]]:
    station_dir = raw_data_root() / "stations"
    candidates = sorted(station_dir.glob("stations_*.json"))
    if not candidates:
        raise FileNotFoundError(
            "No raw station payload found. Run `python3 -m src.ingestion.cli stations` first."
        )

    latest_path = candidates[-1]
    with latest_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload.get("fuel_stations", [])


def latest_station_file() -> Path | None:
    station_dir = raw_data_root() / "stations"
    candidates = sorted(station_dir.glob("stations_*.json"))
    return candidates[-1] if candidates else None
