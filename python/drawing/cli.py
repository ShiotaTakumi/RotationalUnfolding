"""
CLI interface for drawing utility.

Provides command-line interface for visualizing JSONL outputs.
JSONL 出力を可視化するコマンドラインインターフェース。
"""

import argparse
import sys
from pathlib import Path

from drawing.draw_raw import draw_raw_jsonl
from poly_resolve import find_repo_root, resolve_poly


def resolve_drawing_paths(repo_root, poly_id, output_type):
    """
    Resolves paths for input JSONL and output directory based on polyhedron and type.

    polyhedron 指定と type から入力 JSONL と出力ディレクトリのパスを解決する。

    Args:
        repo_root (Path): Repository root path.
        poly_id (str): Polyhedron identifier (path or logical name).
        output_type (str): Output type ("raw", "noniso", "exact").

    Returns:
        tuple: (input_jsonl_path, svg_output_dir, poly_class, poly_name)

    Raises:
        FileNotFoundError: If input JSONL does not exist.
    """
    _data_dir, output_dir, poly_class, poly_name = resolve_poly(repo_root, poly_id)

    # Determine input JSONL path based on type
    # type に基づいて入力 JSONL のパスを決定
    if output_type == "raw":
        input_jsonl = output_dir / "raw.jsonl"
    elif output_type == "noniso":
        input_jsonl = output_dir / "noniso.jsonl"
    elif output_type == "exact":
        input_jsonl = output_dir / "exact.jsonl"
    else:
        raise ValueError(f"Unknown output type: {output_type}")

    if not input_jsonl.is_file():
        raise FileNotFoundError(
            f"Input JSONL not found: {input_jsonl}\n"
            f"Make sure to run the appropriate phase first."
        )

    svg_output_dir = output_dir / "draw" / output_type

    return input_jsonl, svg_output_dir, poly_class, poly_name


def create_parser():
    """
    Creates and returns the argument parser for the drawing CLI.
    
    描画 CLI 用の引数パーサを作成して返す。
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="drawing",
        description="Drawing utility for visualizing rotational unfolding outputs",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Draw SVG files from JSONL output"
    )
    
    run_parser.add_argument(
        "--type",
        required=True,
        choices=["raw", "noniso", "exact"],
        help="Output type to visualize (raw: Phase 1, noniso: Phase 2, exact: Phase 3)"
    )
    
    run_parser.add_argument(
        "--poly",
        required=True,
        help="Path to polyhedron data directory (e.g., data/polyhedra/archimedean/s07)"
    )
    
    run_parser.add_argument(
        "--no-labels",
        action="store_true",
        default=False,
        help="Hide face and edge labels (draw polygons only)"
    )
    
    return parser


def main():
    """
    Main entry point for the drawing CLI.
    
    描画 CLI のメイン入口。
    
    Example usage:
        PYTHONPATH=python python -m drawing run --type raw --poly polyhedra/archimedean/s07
        PYTHONPATH=python python -m drawing run --type noniso --poly polyhedra/platonic/r01
        PYTHONPATH=python python -m drawing run --type exact --poly polyhedra/johnson/n20
    
    Execution model:
        すべての実行は cwd 非依存で、リポジトリルートを基準にパスを解決する。
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
            
            # Resolve paths
            # パスを解決
            input_jsonl, output_dir, poly_class, poly_name = resolve_drawing_paths(
                repo_root, args.poly, args.type
            )
            
            show_labels = not args.no_labels
            
            label_status = "no labels" if args.no_labels else "with labels"
            print(f"Drawing {args.type} output for: {args.poly} ({label_status})")
            print(f"Input: {input_jsonl}")
            print(f"Output: {output_dir}/")
            print("")
            
            # Draw
            # 描画
            num_generated = draw_raw_jsonl(input_jsonl, output_dir, show_labels=show_labels)
            print(f"Done. Generated {num_generated} SVG files.")
            
            sys.exit(0)
        
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
