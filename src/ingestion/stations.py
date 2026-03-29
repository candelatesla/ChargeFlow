from __future__ import annotations

from typing import Any

from src.utils.config import get_settings, load_base_config
from src.utils.http import get_json


def fetch_station_metadata() -> dict[str, Any]:
    config = load_base_config()
    settings = get_settings()

    params = {
        "api_key": settings.nrel_api_key,
        "fuel_type": "ELEC",
        "status": "E",
        "state": ",".join(config["defaults"]["states"]),
        "limit": config["defaults"]["station_limit"],
    }
    url = config["sources"]["nrel"]["base_url"]
    payload = get_json(url, params=params)
    payload["chargeflow_metadata"] = {
        "source": "nrel_alt_fuel_stations",
        "states": config["defaults"]["states"],
    }
    return payload
