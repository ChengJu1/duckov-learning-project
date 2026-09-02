"""Command-line entry point for ``python -m duckov_game``."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from duckov_game.app import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Duckov Learning Project")
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="stop after this many frames; intended for automated smoke tests",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(max_frames=args.max_frames)


if __name__ == "__main__":
    raise SystemExit(main())

