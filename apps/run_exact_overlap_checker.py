#!/usr/bin/env python3

import os
import sys
import subprocess

# exact_overlap_checker.py のラッパー用スクリプト
# Wrapper script for exact_overlap_checker.py

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_list.ini>")
        sys.exit(1)

    ini_file = sys.argv[1]
    if not os.path.isfile(ini_file):
        print(f"Error: .ini file not found: {ini_file}")
        sys.exit(1)

    # .ini ファイルを読み込み
    # Read paths from the .ini file
    expr_path = ""
    exact_path = ""
    with open(ini_file) as f:
        for line in f:
            if line.startswith("expr_path"):
                expr_path = line.split("=", 1)[1].strip()
            elif line.startswith("exact_path"):
                exact_path= line.split("=", 1)[1].strip()

    if not expr_path or not exact_path:
        print("Error: Missing required paths in the .ini file")
        sys.exit(1)

    # scripts/exact_overlap_checker.py への相対パスを指定
    # （必要に応じてパスの場所を変更）
    # Specify the relative path to scripts/exact_overlap_checker.py
    # (modify the path as needed)
    script_path = os.path.join(os.path.dirname(__file__), "../scripts/exact_overlap_checker.py")

    if not os.path.isfile(script_path):
        print(f"Error: exact_overlap_checker.py not found at {script_path}")
        sys.exit(1)

    # exact_overlap_checker.py を実行
    # Execute exact_overlap_checker.py
    try:
        subprocess.run(["python3", script_path, expr_path, exact_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute exact_overlap_checker.py.")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
