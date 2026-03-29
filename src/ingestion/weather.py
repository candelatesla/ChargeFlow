from __future__ import annotations

from typing import Any

from src.utils.config import load_base_config
from src.utils.http import get_json


def fetch_weather_context() -> dict[str, Any]:
    config = load_base_config()
    base_url = config["sources"]["weather"]["base_url"]
    hourly_fields = ",".join(config["sources"]["weather"]["hourly_fields"])

    weather_payloads: list[dict[str, Any]] = []
    for region in config["regions"]["weather"]:
        params = {
            "latitude": region["latitude"],
            "longitude": region["longitude"],
            "hourly": hourly_fields,
            "timezone": "America/Chicago",
            "forecast_days": 3,
        }
        payload = get_json(base_url, params=params)
        payload["chargeflow_metadata"] = {
            "station_group": region["station_group"],
            "source": "open_meteo",
        }
        weather_payloads.append(payload)

    return {"records": weather_payloads}
