from __future__ import annotations

from typing import Any

from src.utils.config import get_settings, load_base_config
from src.utils.http import get_json


def fetch_energy_context() -> dict[str, Any]:
    config = load_base_config()
    settings = get_settings()
    source_config = config["sources"]["eia"]

    params: dict[str, Any] = {
        "api_key": settings.eia_api_key,
        "frequency": source_config["frequency"],
        "data[0]": source_config["data"][0],
    }

    for respondent in config["regions"]["energy"]["respondents"]:
        params.setdefault("facets[respondent][]", [])
        params["facets[respondent][]"].append(respondent)

    for value_type in source_config["facets"]["type"]:
        params.setdefault("facets[type][]", [])
        params["facets[type][]"].append(value_type)

    for index, item in enumerate(source_config["sort"]):
        params[f"sort[{index}][column]"] = item["column"]
        params[f"sort[{index}][direction]"] = item["direction"]

    payload = get_json(source_config["base_url"], params=params)
    payload["chargeflow_metadata"] = {
        "source": "eia_region_data",
        "respondents": config["regions"]["energy"]["respondents"],
    }
    return payload
