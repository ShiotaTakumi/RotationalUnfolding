#!/usr/bin/env python3

import os
import sys
import subprocess

# generate_exact_expressions.py のラッパー用スクリプト
# Wrapper script for generate_exact_expressions.py

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
    adj_path = ""
    noniso_path = ""
    expr_path = ""
    with open(ini_file) as f:
        for line in f:
            if line.startswith("adj_path"):
                adj_path = line.split("=", 1)[1].strip()
            elif line.startswith("noniso_path"):
                noniso_path = line.split("=", 1)[1].strip()
            elif line.startswith("expr_path"):
                expr_path = line.split("=", 1)[1].strip()

    if not adj_path or not noniso_path or not expr_path:
        print("Error: Missing required paths in the .ini file")
        sys.exit(1)

    # scripts/generate_exact_expressions.py への相対パスを指定
    # （必要に応じてパスの場所を変更）
    # Specify the relative path to scripts/generate_exact_expressions.py
    # (modify the path as needed)
    script_path = os.path.join(os.path.dirname(__file__), "../scripts/generate_exact_expressions.py")

    if not os.path.isfile(script_path):
        print(f"Error: generate_exact_expressions.py not found at {script_path}")
        sys.exit(1)

    # generate_exact_expressions.py を実行
    # Execute generate_exact_expressions.py
    subprocess.run(["python3", script_path, adj_path, noniso_path, expr_path], check=True)

if __name__ == "__main__":
    main()
