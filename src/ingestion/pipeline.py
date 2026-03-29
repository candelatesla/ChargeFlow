from __future__ import annotations

import logging
from pathlib import Path

from src.ingestion.energy import fetch_energy_context
from src.ingestion.stations import fetch_station_metadata
from src.ingestion.weather import fetch_weather_context
from src.utils.filesystem import write_json


LOGGER = logging.getLogger(__name__)


def pull_stations() -> Path:
    payload = fetch_station_metadata()
    output_path = write_json(payload, "stations", "stations")
    LOGGER.info("Saved station metadata to %s", output_path)
    return output_path


def pull_weather() -> Path:
    payload = fetch_weather_context()
    output_path = write_json(payload, "weather", "weather")
    LOGGER.info("Saved weather context to %s", output_path)
    return output_path


def pull_energy() -> Path:
    payload = fetch_energy_context()
    output_path = write_json(payload, "energy", "energy")
    LOGGER.info("Saved energy context to %s", output_path)
    return output_path


def pull_all() -> list[Path]:
    return [pull_stations(), pull_weather(), pull_energy()]
