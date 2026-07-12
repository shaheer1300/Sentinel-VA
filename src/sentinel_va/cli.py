from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import execute


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute gated Sentinel-VA Norfolk pilot phases")
    parser.add_argument("--config", default="configs/norfolk_pilot.json")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--execution-config", default="configs/norfolk_phase4_7.json")
    parser.add_argument("--from-phase", type=int, choices=range(0, 8), required=True)
    parser.add_argument("--through-phase", type=int, choices=range(0, 8), required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.from_phase > args.through_phase:
        raise SystemExit("--from-phase may not exceed --through-phase")
    root = Path.cwd()
    run_dir = execute(
        root,
        root / args.config,
        args.run_id,
        args.from_phase,
        args.through_phase,
        root / args.execution_config,
    )
    print(run_dir)


if __name__ == "__main__":
    main()
