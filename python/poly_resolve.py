"""
Shared polyhedron resolution logic.

Provides find_repo_root() and resolve_poly() used by all CLI modules.
全 CLI モジュール共通のリポジトリルート探索と --poly 引数解決ロジック。
"""

from pathlib import Path


def find_repo_root():
    """
    Finds the repository root by searching upward for the '.git' directory.

    .git ディレクトリを上方向に探索してリポジトリルートを見つける。

    Returns:
        Path: Absolute path to the repository root.

    Raises:
        RuntimeError: If the repository root cannot be found.
    """
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    raise RuntimeError("Could not find repository root (.git directory)")


def resolve_poly(repo_root, poly_id):
    """
    Resolve a --poly directory path to data/output directories and class/name.

    --poly は polyhedron データディレクトリへのパスを直接受け取る。
    相対パス・絶対パスの両方を受け付ける。
    相対パスは cwd → repo_root の順に解決を試みる。

    Args:
        repo_root (Path): Repository root path.
        poly_id (str): Path to polyhedron data directory
                        (e.g. "data/polyhedra/archimedean/s12L").

    Returns:
        tuple: (data_dir, output_dir, poly_class, poly_name)
            - data_dir (Path):   Absolute path to polyhedron data directory
            - output_dir (Path): Absolute path to output directory
            - poly_class (str):  Polyhedron class  (e.g. "archimedean")
            - poly_name (str):   Polyhedron name   (e.g. "s12L")

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    poly_path = Path(poly_id)

    # Resolve: try as-is (absolute or relative to cwd), then relative to repo_root
    if poly_path.is_dir():
        data_dir = poly_path.resolve()
    elif (repo_root / poly_path).is_dir():
        data_dir = (repo_root / poly_path).resolve()
    else:
        raise FileNotFoundError(
            f"Polyhedron directory not found: {poly_id}\n"
            f"Provide a valid path to the polyhedron data directory "
            f"(e.g. data/polyhedra/archimedean/s12L)"
        )

    poly_name = data_dir.name
    poly_class = data_dir.parent.name

    output_dir = repo_root / "output" / "polyhedra" / poly_class / poly_name

    return data_dir, output_dir, poly_class, poly_name
