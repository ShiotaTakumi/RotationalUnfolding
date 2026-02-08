"""
Entry point for `python -m run_all`.

Executes the full rotational unfolding pipeline:
    Phase 1 (raw.jsonl) → Phase 2 (noniso.jsonl) → Phase 3 (exact.jsonl) → Drawing (exact SVG)

Usage:
    PYTHONPATH=reorg/python python -m run_all --poly polyhedra/<class>/<name>

Example:
    PYTHONPATH=reorg/python python -m run_all --poly polyhedra/archimedean/s07
"""

import argparse
import subprocess
import sys


def create_parser():
    parser = argparse.ArgumentParser(
        prog="run_all",
        description="Run the full rotational unfolding pipeline: Phase 1 → 2 → 3 → Drawing (exact)",
    )
    parser.add_argument(
        "--poly",
        required=True,
        help="Polyhedron path (e.g., polyhedra/archimedean/s07)",
    )
    return parser


def run_step(label, args):
    """Run a subprocess step. Exit immediately on failure."""
    print(f"[run_all] {label}", flush=True)
    result = subprocess.run(
        [sys.executable] + args,
        cwd=None,
    )
    if result.returncode != 0:
        print(f"[run_all] FAILED at: {label} (exit code {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    parser = create_parser()
    args = parser.parse_args()
    poly = args.poly

    print(f"[run_all] Pipeline start: {poly}")
    print(f"[run_all] Python: {sys.executable}")
    print("")

    run_step(
        "Phase 1: rotational_unfolding",
        ["-m", "rotational_unfolding", "run", "--poly", poly],
    )
    print("")

    run_step(
        "Phase 2: nonisomorphic",
        ["-m", "nonisomorphic", "run", "--poly", poly],
    )
    print("")

    run_step(
        "Phase 3: exact",
        ["-m", "exact", "run", "--poly", poly],
    )
    print("")

    run_step(
        "Drawing: exact",
        ["-m", "drawing", "run", "--type", "exact", "--poly", poly],
    )
    print("")

    print(f"[run_all] All steps completed for: {poly}")


if __name__ == "__main__":
    main()
