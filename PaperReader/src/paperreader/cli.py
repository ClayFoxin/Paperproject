"""Command line interface for PaperReader."""
from __future__ import annotations

import argparse
from pathlib import Path

from paperreader.config import load_settings
from paperreader.pipeline.run import run_pipeline
from paperreader.utils.log import get_logger


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PaperReader pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run full pipeline")
    run_parser.add_argument(
        "--env-file", type=Path, default=None, help="Path to .env file containing API keys",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "run":
        settings = load_settings(args.env_file)
        logger.info("Starting pipeline with settings loaded from %s", args.env_file or ".env")
        run_pipeline(settings)


if __name__ == "__main__":
    main()
