"""
CLI interface for exact overlap detection.

Provides command-line interface for Phase 3 processing.
Phase 3 処理のコマンドラインインターフェース。
"""

import argparse
import sys
from pathlib import Path

from exact.exact_overlap import filter_exact_overlaps


def find_repo_root():
    """
    Finds the repository root by searching upward for the 'reorg' directory.

    reorg ディレクトリを上方向に探索してリポジトリルートを見つける。

    Returns:
        Path: Absolute path to the repository root.

    Raises:
        RuntimeError: If the repository root cannot be found.
    """
    current = Path(__file__).resolve().parent
    while current != current.parent:
        reorg_dir = current / "reorg"
        if reorg_dir.is_dir():
            return current
        current = current.parent

    raise RuntimeError("Could not find repository root (reorg/ directory)")


def resolve_paths(repo_root, poly_id):
    """
    Resolves paths for Phase 3 processing.

    Phase 3 処理のためのパスを解決します。

    Args:
        repo_root (Path): Repository root path
        poly_id (str): Polyhedron identifier in CLASS/NAME format

    Returns:
        tuple: (noniso_jsonl_path, polyhedron_json_path, exact_jsonl_path, poly_class, poly_name)

    Raises:
        ValueError: If poly_id format is invalid
        FileNotFoundError: If required input files do not exist
    """
    parts = poly_id.split("/")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid poly_id format: {poly_id}. Expected CLASS/NAME (e.g., archimedean/s07)"
        )

    poly_class, poly_name = parts

    # Input: noniso.jsonl (Phase 2 output)
    # 入力: noniso.jsonl（Phase 2 出力）
    output_dir = repo_root / "reorg" / "output" / "polyhedra" / poly_class / poly_name
    noniso_jsonl_path = output_dir / "noniso.jsonl"

    if not noniso_jsonl_path.is_file():
        raise FileNotFoundError(
            f"noniso.jsonl not found: {noniso_jsonl_path}\n"
            f"Run Phase 2 first: python -m nonisomorphic run --poly {poly_id}"
        )

    # Input: polyhedron.json (polyhedron structure)
    # 入力: polyhedron.json（多面体構造）
    data_dir = repo_root / "reorg" / "data" / "polyhedra" / poly_class / poly_name
    polyhedron_json_path = data_dir / "polyhedron.json"

    if not polyhedron_json_path.is_file():
        raise FileNotFoundError(
            f"polyhedron.json not found: {polyhedron_json_path}"
        )

    # Output: exact.jsonl (Phase 3 output)
    # 出力: exact.jsonl（Phase 3 出力）
    exact_jsonl_path = output_dir / "exact.jsonl"

    return noniso_jsonl_path, polyhedron_json_path, exact_jsonl_path, poly_class, poly_name


def create_parser():
    """
    Creates and returns the argument parser for the exact overlap CLI.

    厳密重なり判定 CLI 用の引数パーサを作成して返す。

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="exact",
        description="Phase 3: Exact overlap detection for rotational unfolding",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Check exact overlaps in noniso.jsonl and produce exact.jsonl"
    )

    run_parser.add_argument(
        "--poly",
        required=True,
        help="Polyhedron identifier in CLASS/NAME format (e.g., archimedean/s07)"
    )

    return parser


def main():
    """
    Main entry point for the exact overlap detection CLI.

    厳密重なり判定 CLI のメイン入口。

    Example usage:
        PYTHONPATH=reorg/python python -m exact run --poly archimedean/s07
        PYTHONPATH=reorg/python python -m exact run --poly johnson/n20

    Process:
        1. Resolve paths (noniso.jsonl, polyhedron.json, exact.jsonl)
        2. Load polyhedron structure (including vertex incidence)
        3. For each record, reconstruct exact positions and check overlaps
        4. Write non-overlapping records to exact.jsonl

    処理:
        1. パスを解決（noniso.jsonl, polyhedron.json, exact.jsonl）
        2. 多面体構造を読み込む（頂点共有関係を含む）
        3. 各レコードについて厳密座標を再構築し重なりを判定
        4. 重なりのないレコードを exact.jsonl に書き出す

    Output location:
        exact.jsonl is written to reorg/output/polyhedra/<class>/<name>/
        This is the same directory as noniso.jsonl (Phase 2 output).

    出力場所:
        exact.jsonl は reorg/output/polyhedra/<class>/<name>/ に書き込まれる。
        これは noniso.jsonl（Phase 2 出力）と同じディレクトリです。
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        try:
            # Find repository root
            # リポジトリルートを見つける
            repo_root = find_repo_root()
            print(f"Repository root: {repo_root}")

            # Resolve paths
            # パスを解決
            noniso_jsonl_path, polyhedron_json_path, exact_jsonl_path, poly_class, poly_name = resolve_paths(
                repo_root, args.poly
            )

            print(f"Phase 3: Exact overlap detection for {args.poly}")
            print(f"Input (noniso.jsonl): {noniso_jsonl_path}")
            print(f"Polyhedron structure: {polyhedron_json_path}")
            print(f"Output (exact.jsonl): {exact_jsonl_path}")
            print("")

            # Run exact overlap detection
            # 厳密重なり判定を実行
            print("Checking exact overlaps...")
            num_input, num_output = filter_exact_overlaps(
                noniso_jsonl_path,
                polyhedron_json_path,
                exact_jsonl_path
            )

            print("")
            print(f"Input records (noniso.jsonl): {num_input}")
            print(f"Output records (exact.jsonl): {num_output}")
            print(f"Removed overlapping: {num_input - num_output}")
            print("")
            print("Done.")

            sys.exit(0)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
