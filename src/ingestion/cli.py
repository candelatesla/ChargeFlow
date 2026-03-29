from __future__ import annotations

import argparse
import logging

from src.ingestion.pipeline import pull_all, pull_energy, pull_stations, pull_weather
from src.utils.logging import configure_logging


LOGGER = logging.getLogger(__name__)


def _setup() -> None:
    configure_logging()

def stations_command() -> None:
    _setup()
    output_path = pull_stations()
    LOGGER.info("Station ingestion complete: %s", output_path)


def weather_command() -> None:
    _setup()
    output_path = pull_weather()
    LOGGER.info("Weather ingestion complete: %s", output_path)


def energy_command() -> None:
    _setup()
    output_path = pull_energy()
    LOGGER.info("Energy ingestion complete: %s", output_path)


def pull_all_command() -> None:
    _setup()
    output_paths = pull_all()
    LOGGER.info("Full ingestion complete: %s", output_paths)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ChargeFlow Day 1 ingestion commands.")
    parser.add_argument(
        "command",
        choices=["stations", "weather", "energy", "pull-all"],
        help="Which ingestion pipeline to run.",
    )
    return parser

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "stations": stations_command,
        "weather": weather_command,
        "energy": energy_command,
        "pull-all": pull_all_command,
    }
    handlers[args.command]()


if __name__ == "__main__":
    main()
