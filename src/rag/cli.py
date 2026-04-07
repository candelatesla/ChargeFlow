from __future__ import annotations

import argparse
import logging

from src.rag.service import build_rag_index
from src.utils.logging import configure_logging


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ChargeFlow Day 5 retrieval commands.")
    parser.add_argument(
        "command",
        choices=["build-index"],
        help="Which retrieval pipeline to run.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging()

    if args.command == "build-index":
        outputs = build_rag_index()
        LOGGER.info("RAG index build complete: %s", outputs)


if __name__ == "__main__":
    main()
