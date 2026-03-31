from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.utils.filesystem import raw_data_root, processed_data_root


def latest_raw_station_rows() -> list[dict[str, Any]]:
    path = _latest_file(raw_data_root() / "stations", "stations_*.json")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    rows = []
    for station in payload.get("fuel_stations", []):
        rows.append(
            {
                "source_station_id": str(station.get("id", "")),
                "station_name": station.get("station_name"),
                "city": station.get("city"),
                "state": station.get("state"),
                "access_code": station.get("access_code"),
                "ev_network": station.get("ev_network"),
                "ev_connector_types": "|".join(station.get("ev_connector_types") or []),
                "latitude": station.get("latitude"),
                "longitude": station.get("longitude"),
                "ev_level2_evse_num": _to_int(station.get("ev_level2_evse_num")),
                "ev_dc_fast_num": _to_int(station.get("ev_dc_fast_num")),
                "ev_charging_units": _to_int(station.get("ev_charging_units")),
            }
        )
    return rows


def latest_raw_weather_rows() -> list[dict[str, Any]]:
    path = _latest_file(raw_data_root() / "weather", "weather_*.json")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    rows = []
    for record in payload.get("records", []):
        metadata = record.get("chargeflow_metadata", {})
        station_group = metadata.get("station_group", "unknown")
        state = station_group.split("_")[-1].upper()
        hourly = record.get("hourly", {})
        times = hourly.get("time", [])
        for idx, timestamp in enumerate(times):
            rows.append(
                {
                    "station_group": station_group,
                    "state": state,
                    "observation_ts_utc": timestamp,
                    "temperature_2m": _at(hourly.get("temperature_2m"), idx),
                    "apparent_temperature": _at(hourly.get("apparent_temperature"), idx),
                    "precipitation_probability": _at(hourly.get("precipitation_probability"), idx),
                    "cloud_cover": _at(hourly.get("cloud_cover"), idx),
                    "wind_speed_10m": _at(hourly.get("wind_speed_10m"), idx),
                }
            )
    return rows


def latest_raw_energy_rows() -> list[dict[str, Any]]:
    path = _latest_file(raw_data_root() / "energy", "energy_*.json")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    rows = []
    for item in payload.get("response", {}).get("data", []):
        respondent = item.get("respondent", "")
        rows.append(
            {
                "respondent": respondent,
                "state": _map_respondent_to_state(respondent),
                "period_utc": item.get("period"),
                "value": _to_float(item.get("value")),
                "value_type": item.get("type"),
            }
        )
    return rows


def synthetic_csv_rows(file_name: str) -> list[dict[str, Any]]:
    path = processed_data_root() / "synthetic" / file_name
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _latest_file(directory: Path, pattern: str) -> Path:
    candidates = sorted(directory.glob(pattern))
    if not candidates:
        raise FileNotFoundError(f"No files found for pattern {pattern} in {directory}.")
    return candidates[-1]


def _map_respondent_to_state(respondent: str) -> str:
    mapping = {"ERCO": "TX", "CISO": "CA"}
    return mapping.get(respondent, "NA")


def _to_int(value: Any) -> int:
    if value in (None, "", []):
        return 0
    if isinstance(value, list):
        return len(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _at(values: list[Any] | None, index: int) -> Any:
    if not values or index >= len(values):
        return None
    return values[index]
