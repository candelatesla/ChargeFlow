from __future__ import annotations

import argparse
import logging

from src.synthetic.pipeline import generate_synthetic_data
from src.utils.logging import configure_logging


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ChargeFlow Day 2 synthetic data commands.")
    parser.add_argument(
        "command",
        choices=["generate-all"],
        help="Which synthetic data pipeline to run.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging()

    if args.command == "generate-all":
        outputs = generate_synthetic_data()
        LOGGER.info("Synthetic generation complete: %s", outputs)


if __name__ == "__main__":
    main()
