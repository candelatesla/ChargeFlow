from __future__ import annotations

import argparse
import logging

from src.ml.pipeline import run_ml_pipeline
from src.utils.logging import configure_logging


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ChargeFlow Day 4 analytics and ML commands.")
    parser.add_argument(
        "command",
        choices=["run-all"],
        help="Which ML pipeline to run.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging()

    if args.command == "run-all":
        outputs = run_ml_pipeline()
        LOGGER.info("ML pipeline complete: %s", outputs)


if __name__ == "__main__":
    main()
