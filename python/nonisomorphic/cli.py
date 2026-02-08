"""
CLI interface for nonisomorphic filtering.

Provides command-line interface for Phase 2 processing.
Phase 2 処理のコマンドラインインターフェース。
"""

import argparse
import sys
from pathlib import Path

from nonisomorphic.remove_isomorphic import remove_isomorphic_duplicates
from poly_resolve import find_repo_root, resolve_poly


def create_parser():
    """
    Creates and returns the argument parser for the nonisomorphic CLI.
    
    非同型除去 CLI 用の引数パーサを作成して返す。
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="nonisomorphic",
        description="Phase 2: Nonisomorphic filtering for rotational unfolding",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Remove isomorphic duplicates from raw.jsonl"
    )
    
    run_parser.add_argument(
        "--poly",
        required=True,
        help="Path to polyhedron data directory (e.g., data/polyhedra/archimedean/s04)"
    )
    
    return parser


def main():
    """
    Main entry point for the nonisomorphic filtering CLI.
    
    非同型フィルタリング CLI のメイン入口。
    
    Example usage:
        PYTHONPATH=python python -m nonisomorphic run --poly polyhedra/archimedean/s04
        PYTHONPATH=python python -m nonisomorphic run --poly polyhedra/platonic/r01
    
    Process:
        1. Resolve paths (raw.jsonl, polyhedron.json, noniso.jsonl)
        2. Load polyhedron structure
        3. Remove isomorphic duplicates
        4. Write filtered output to noniso.jsonl
    
    処理:
        1. パスを解決（raw.jsonl, polyhedron.json, noniso.jsonl）
        2. 多面体構造を読み込む
        3. 同型な重複を除去
        4. フィルタリング後の出力を noniso.jsonl に書き出す
    
    Output location:
        noniso.jsonl is written to output/polyhedra/<class>/<name>/
        This is the same directory as raw.jsonl (Phase 1 output).
    
    出力場所:
        noniso.jsonl は output/polyhedra/<class>/<name>/ に書き込まれる。
        これは raw.jsonl（Phase 1 出力）と同じディレクトリです。
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
            data_dir, output_dir, poly_class, poly_name = resolve_poly(repo_root, args.poly)
            
            raw_jsonl_path = output_dir / "raw.jsonl"
            if not raw_jsonl_path.is_file():
                raise FileNotFoundError(
                    f"raw.jsonl not found: {raw_jsonl_path}\n"
                    f"Run Phase 1 first: python -m rotational_unfolding run --poly {args.poly}"
                )
            
            polyhedron_json_path = data_dir / "polyhedron.json"
            if not polyhedron_json_path.is_file():
                raise FileNotFoundError(f"polyhedron.json not found: {polyhedron_json_path}")
            
            noniso_jsonl_path = output_dir / "noniso.jsonl"
            
            print(f"Phase 2: Nonisomorphic filtering for {args.poly}")
            print(f"Input (raw.jsonl): {raw_jsonl_path}")
            print(f"Polyhedron structure: {polyhedron_json_path}")
            print(f"Output (noniso.jsonl): {noniso_jsonl_path}")
            print("")
            
            # Remove isomorphic duplicates
            # 同型な重複を除去
            print("Removing isomorphic duplicates...")
            num_input, num_output = remove_isomorphic_duplicates(
                raw_jsonl_path,
                polyhedron_json_path,
                noniso_jsonl_path
            )
            
            print("")
            print(f"Input records (raw.jsonl): {num_input}")
            print(f"Output records (noniso.jsonl): {num_output}")
            print(f"Removed duplicates: {num_input - num_output}")
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
