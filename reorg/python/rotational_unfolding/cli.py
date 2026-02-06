"""
CLI interface for rotational unfolding.

Provides the command-line interface for running rotational unfolding
on polyhedra using the C++ core as a subprocess.

CLI の入口を提供し、C++ コアをサブプロセスとして呼び出す。
"""

import argparse
import sys
from pathlib import Path

from rotational_unfolding.runner import run_rotational_unfolding


def create_parser():
    """
    Creates and returns the argument parser for the CLI.
    
    CLI 用の引数パーサを作成して返す。
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="rotational_unfolding",
        description="Rotational unfolding algorithm CLI (Phase 1)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run rotational unfolding for a polyhedron"
    )
    
    run_parser.add_argument(
        "--poly",
        required=True,
        help="Polyhedron identifier in CLASS/NAME format (e.g., archimedean/s05)"
    )
    
    run_parser.add_argument(
        "--out",
        required=True,
        help="Output directory (e.g., outputs/)"
    )
    
    run_parser.add_argument(
        "--symmetric",
        choices=["auto", "on", "off"],
        default="auto",
        help="Symmetry mode (default: auto)"
    )
    
    return parser


def main():
    """
    Main entry point for the CLI.
    
    CLI のメイン入口。
    
    Example usage:
        python -m rotational_unfolding run --poly archimedean/s05 --out outputs/
        python -m rotational_unfolding run --poly archimedean/s01 --out outputs/ --symmetric on
    """
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "run":
        try:
            success = run_rotational_unfolding(
                poly_id=args.poly,
                output_dir=args.out,
                symmetric_mode=args.symmetric
            )
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
