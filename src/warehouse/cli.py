from __future__ import annotations

import argparse
import logging

from src.utils.logging import configure_logging
from src.warehouse.pipeline import build_warehouse


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ChargeFlow Day 3 warehouse commands.")
    parser.add_argument(
        "command",
        choices=["build-all"],
        help="Which warehouse pipeline to run.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging()

    if args.command == "build-all":
        outputs = build_warehouse()
        LOGGER.info("Warehouse build complete: %s", outputs)


if __name__ == "__main__":
    main()
