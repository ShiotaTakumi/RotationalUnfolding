"""
CLI interface for drawing utility.

Provides command-line interface for visualizing JSONL outputs.
JSONL 出力を可視化するコマンドラインインターフェース。
"""

import argparse
import sys
from pathlib import Path

from drawing.draw_raw import draw_raw_jsonl


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


def resolve_poly_paths(repo_root, poly_id, output_type):
    """
    Resolves paths for input JSONL and output directory based on polyhedron path and type.
    
    polyhedron パスと type から入力 JSONL と出力ディレクトリのパスを解決する。
    
    Args:
        repo_root (Path): Repository root path.
        poly_id (str): Polyhedron path (e.g., "polyhedra/archimedean/s07").
        output_type (str): Output type ("raw", "noniso", "exact").
    
    Returns:
        tuple: (input_jsonl_path, output_dir_path, poly_class, poly_name)
    
    Raises:
        ValueError: If poly_id path does not contain at least class/name.
        FileNotFoundError: If input JSONL does not exist.
    """
    poly_path = Path(poly_id)
    if len(poly_path.parts) < 2:
        raise ValueError(
            f"Invalid poly path: {poly_id}. "
            f"Expected a path with at least class/name (e.g., polyhedra/archimedean/s07)"
        )
    
    poly_name = poly_path.name
    poly_class = poly_path.parent.name
    
    # Base output directory for this polyhedron
    # この多面体の基本出力ディレクトリ
    base_dir = repo_root / "reorg" / "output" / poly_path
    
    # Determine input JSONL path based on type
    # type に基づいて入力 JSONL のパスを決定
    if output_type == "raw":
        input_jsonl = base_dir / "raw.jsonl"
    elif output_type == "noniso":
        input_jsonl = base_dir / "noniso.jsonl"
    elif output_type == "exact":
        input_jsonl = base_dir / "exact.jsonl"
    else:
        raise ValueError(f"Unknown output type: {output_type}")
    
    # Check if input JSONL exists
    # 入力 JSONL の存在を確認
    if not input_jsonl.is_file():
        raise FileNotFoundError(
            f"Input JSONL not found: {input_jsonl}\n"
            f"Make sure to run the appropriate phase first."
        )
    
    # Output directory for SVG files
    # SVG ファイルの出力ディレクトリ
    output_dir = base_dir / "draw" / output_type
    
    return input_jsonl, output_dir, poly_class, poly_name


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
        help="Polyhedron path (e.g., polyhedra/archimedean/s07)"
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
        PYTHONPATH=reorg/python python -m drawing run --type raw --poly polyhedra/archimedean/s07
        PYTHONPATH=reorg/python python -m drawing run --type noniso --poly polyhedra/platonic/r01
        PYTHONPATH=reorg/python python -m drawing run --type exact --poly polyhedra/johnson/n20
    
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
            input_jsonl, output_dir, poly_class, poly_name = resolve_poly_paths(
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
