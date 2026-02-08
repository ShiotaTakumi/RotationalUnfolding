"""
Runner module for executing rotational unfolding.

Handles:
- Path resolution for polyhedron data
- C++ binary invocation via subprocess
- raw.jsonl generation (canonical output per polyhedron)
- run.json generation (experiment metadata)

実行ロジックを提供：
- 多面体データのパス解決
- C++ バイナリのサブプロセス呼び出し
- raw.jsonl 生成（多面体ごとの正規出力）
- run.json 生成（実験メタデータ）
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from poly_resolve import find_repo_root, resolve_poly


def find_cpp_binary(repo_root):
    """
    Locates the C++ binary (rotunfold) in the repository.
    
    リポジトリ内の C++ バイナリ（rotunfold）を見つける。
    
    Args:
        repo_root (Path): Repository root path.
    
    Returns:
        Path: Absolute path to the rotunfold binary.
    
    Raises:
        FileNotFoundError: If the binary does not exist.
    """
    cpp_binary = repo_root / "cpp" / "rotunfold"
    
    if not cpp_binary.is_file():
        raise FileNotFoundError(
            f"C++ binary not found: {cpp_binary}. "
            "Please build the C++ code first (cd cpp && make)."
        )
    
    return cpp_binary



def generate_run_id():
    """
    Generates a run ID based on timestamp (for run.json metadata only).
    
    タイムスタンプに基づいて実行IDを生成（run.json メタデータ用のみ）。
    
    Returns:
        str: Run ID in the format YYYY-MM-DDTHHMMSSZ
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def load_json_metadata(json_path):
    """
    Loads metadata from a JSON file.
    
    JSON ファイルからメタデータを読み込む。
    
    Args:
        json_path (Path): Path to the JSON file.
    
    Returns:
        dict: Parsed JSON content.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def count_jsonl_records(jsonl_path):
    """
    Counts the number of records in a JSONL file.
    
    JSONL ファイル内のレコード数をカウントする。
    
    Args:
        jsonl_path (Path): Path to the JSONL file.
    
    Returns:
        int: Number of records (lines) in the file.
    """
    if not jsonl_path.is_file():
        return 0
    
    with open(jsonl_path, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def create_run_metadata(
    run_id,
    started_at,
    finished_at,
    exit_code,
    cpp_binary,
    argv,
    cwd,
    polyhedron_json,
    root_pairs_json,
    poly_class,
    poly_name,
    symmetric_mode,
    raw_jsonl_path,
    num_records
):
    """
    Creates the run.json metadata structure.
    
    run.json メタデータ構造を作成する。
    
    Args:
        run_id (str): Unique run identifier.
        started_at (str): ISO8601 UTC timestamp of run start.
        finished_at (str): ISO8601 UTC timestamp of run end.
        exit_code (int): Exit code of the C++ process.
        cpp_binary (Path): Path to the C++ binary.
        argv (list): Command-line arguments passed to C++.
        cwd (str): Current working directory at invocation.
        polyhedron_json (Path): Path to polyhedron.json.
        root_pairs_json (Path): Path to root_pairs.json.
        poly_class (str): Polyhedron class.
        poly_name (str): Polyhedron name.
        symmetric_mode (str): Symmetry mode requested.
        raw_jsonl_path (Path): Path to raw.jsonl output.
        num_records (int): Number of records written to raw.jsonl.
    
    Returns:
        dict: run.json metadata structure.
    """
    # Load input metadata
    polyhedron_data = load_json_metadata(polyhedron_json)
    root_pairs_data = load_json_metadata(root_pairs_json)
    
    # Determine symmetric_used based on mode
    symmetric_used = None
    auto_basis = None
    
    if symmetric_mode == "on":
        symmetric_used = True
    elif symmetric_mode == "off":
        symmetric_used = False
    elif symmetric_mode == "auto":
        # For auto mode, we need to infer from poly_name (same logic as C++)
        # This should match IOUtil::isSymmetricFromPolyName
        if poly_name:
            prefix = poly_name[0]
            if prefix in ['a', 'p', 'r']:
                symmetric_used = True
            elif prefix == 's' and len(poly_name) >= 3:
                try:
                    num = int(poly_name[1:3])
                    symmetric_used = (1 <= num <= 11)
                except ValueError:
                    symmetric_used = False
            else:
                symmetric_used = False
        else:
            symmetric_used = False
        
        auto_basis = {"poly_name": poly_name}
    
    return {
        "schema_version": 1,
        "record_type": "run_metadata",
        "run": {
            "run_id": run_id,
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "exit_code": exit_code
        },
        "command": {
            "executable_path": str(cpp_binary.resolve()),
            "argv": argv,
            "cwd": cwd
        },
        "inputs": {
            "polyhedron": {
                "path": str(polyhedron_json.resolve()),
                "schema_version": polyhedron_data.get("schema_version", 1),
                "poly_class": poly_class,
                "poly_name": poly_name,
                "num_faces": len(polyhedron_data.get("faces", []))
            },
            "root_pairs": {
                "path": str(root_pairs_json.resolve()),
                "schema_version": root_pairs_data.get("schema_version", 1),
                "num_root_pairs": len(root_pairs_data.get("root_pairs", []))
            }
        },
        "options": {
            "symmetric": {
                "mode_requested": symmetric_mode,
                "symmetric_used": symmetric_used,
                **({"auto_basis": auto_basis} if auto_basis else {})
            }
        },
        "outputs": {
            "raw_jsonl": {
                "path": str(raw_jsonl_path.resolve()),
                "schema_version": 1,
                "record_type": "partial_unfolding",
                "num_records_written": num_records
            }
        }
    }


def run_rotational_unfolding(poly_id, symmetric_mode):
    """
    Runs rotational unfolding for a specified polyhedron.
    
    指定された多面体について回転展開を実行する。
    
    Args:
        poly_id (str): Path to polyhedron data directory (e.g., "data/polyhedra/archimedean/s05").
        symmetric_mode (str): Symmetry mode (auto, on, or off).
    
    Returns:
        bool: True if successful, False otherwise.
    
    Workflow:
        1. Resolve paths (polyhedron data, C++ binary)
        2. Create canonical output directory: output/<poly_path>/
        3. Invoke C++ binary to generate raw.jsonl
        4. Generate run.json metadata
        5. Report results
    
    手順:
        1. パス解決（多面体データ、C++ バイナリ）
        2. 正規出力ディレクトリを作成: output/<poly_path>/
        3. C++ バイナリを呼び出して raw.jsonl を生成
        4. run.json メタデータを生成
        5. 結果の報告
    
    Output Convention:
        - Output goes to: output/<poly_path>/
        - This path is deterministic and polyhedron-specific
        - Overwriting is allowed (latest run wins)
        - No timestamp-based directories
    
    出力規約:
        - 出力先: output/<poly_path>/
        - このパスは決定的で多面体固有
        - 上書き可能（最新の実行が優先）
        - タイムスタンプベースのディレクトリは使用しない
    """
    print(f"Starting rotational unfolding for: {poly_id}")
    print(f"Symmetry mode: {symmetric_mode}")
    print("")
    
    # Find repository root
    repo_root = find_repo_root()
    print(f"Repository root: {repo_root}")
    
    # Resolve polyhedron paths
    data_dir, output_dir, poly_class, poly_name = resolve_poly(repo_root, poly_id)
    
    polyhedron_json = data_dir / "polyhedron.json"
    root_pairs_json = data_dir / "root_pairs.json"
    
    if not polyhedron_json.is_file():
        raise FileNotFoundError(f"polyhedron.json not found: {polyhedron_json}")
    if not root_pairs_json.is_file():
        raise FileNotFoundError(f"root_pairs.json not found: {root_pairs_json}")
    
    print(f"Polyhedron: {polyhedron_json}")
    print(f"Root pairs: {root_pairs_json}")
    
    # Find C++ binary
    cpp_binary = find_cpp_binary(repo_root)
    print(f"C++ binary: {cpp_binary}")
    print("")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    raw_jsonl_path = output_dir / "raw.jsonl"
    run_json_path = output_dir / "run.json"
    
    print(f"Output directory: {output_dir}")
    print(f"raw.jsonl: {raw_jsonl_path}")
    print(f"run.json: {run_json_path}")
    print("")
    
    # Prepare C++ command
    argv = [
        str(cpp_binary),
        "--polyhedron", str(polyhedron_json),
        "--roots", str(root_pairs_json),
        "--symmetric", symmetric_mode,
        "--out", str(raw_jsonl_path)
    ]
    
    print("Invoking C++ binary...")
    print(f"Command: {' '.join(argv)}")
    print("")
    
    # Record start time
    started_at = datetime.now(timezone.utc).isoformat()
    
    # Execute C++ binary
    try:
        result = subprocess.run(
            argv,
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=False
        )
        exit_code = result.returncode
    except Exception as e:
        print(f"Error executing C++ binary: {e}", file=sys.stderr)
        return False
    
    # Record end time
    finished_at = datetime.now(timezone.utc).isoformat()
    
    print("")
    print(f"C++ process exited with code: {exit_code}")
    
    if exit_code != 0:
        print("Warning: C++ process did not exit successfully.", file=sys.stderr)
    
    # Count records in raw.jsonl
    num_records = count_jsonl_records(raw_jsonl_path)
    print(f"Records written to raw.jsonl: {num_records}")
    
    # Generate run.json
    print("Generating run.json...")
    
    # Generate run_id (timestamp only, for metadata)
    run_id = generate_run_id()
    cwd = str(Path.cwd().resolve())
    
    run_metadata = create_run_metadata(
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        exit_code=exit_code,
        cpp_binary=cpp_binary,
        argv=argv,
        cwd=cwd,
        polyhedron_json=polyhedron_json,
        root_pairs_json=root_pairs_json,
        poly_class=poly_class,
        poly_name=poly_name,
        symmetric_mode=symmetric_mode,
        raw_jsonl_path=raw_jsonl_path,
        num_records=num_records
    )
    
    with open(run_json_path, "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    print(f"run.json written: {run_json_path}")
    print("")
    print("Done.")
    
    return exit_code == 0
