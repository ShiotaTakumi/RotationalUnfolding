"""
Entry point for `python -m run_all`.

Executes the full rotational unfolding pipeline:
    Phase 1 (raw.jsonl) → Phase 2 (noniso.jsonl) → Phase 3 (exact.jsonl) → Drawing (exact SVG)

Usage:
    PYTHONPATH=python python -m run_all --poly polyhedra/<class>/<name>
    PYTHONPATH=python python -m run_all --poly polyhedra/<class>/<name> --no-labels

Example:
    PYTHONPATH=python python -m run_all --poly polyhedra/archimedean/s07
    PYTHONPATH=python python -m run_all --poly polyhedra/archimedean/s07 --no-labels
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
    parser.add_argument(
        "--no-labels",
        action="store_true",
        default=False,
        help="Hide face and edge labels in exact drawing (passed to drawing phase only)",
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
    no_labels = args.no_labels

    print(f"[run_all] Pipeline start: {poly}")
    print(f"[run_all] Python: {sys.executable}")
    if no_labels:
        print(f"[run_all] Drawing option: --no-labels")
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

    drawing_args = ["-m", "drawing", "run", "--type", "exact", "--poly", poly]
    if no_labels:
        drawing_args.append("--no-labels")

    run_step(
        "Drawing: exact",
        drawing_args,
    )
    print("")

    print(f"[run_all] All steps completed for: {poly}")


if __name__ == "__main__":
    main()
