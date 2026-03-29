from __future__ import annotations

from typing import Any

import requests

from src.utils.config import load_base_config


def get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    config = load_base_config()
    timeout = config["defaults"]["request_timeout_seconds"]
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()
