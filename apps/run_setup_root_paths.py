#!/usr/bin/env python3

import subprocess
import os
import sys

# setup_root_paths.py のラッパー用スクリプト
# Wrapper script for setup_root_paths.py

def main():
    # scripts/setup_root_paths.py への相対パスを指定
    # （必要に応じてパスの場所を変更）
    # Specify the relative path to scripts/setup_root_paths.py
    # (modify the path as needed)
    script_path = os.path.join(os.path.dirname(__file__), "../scripts/setup_root_paths.py")

    if not os.path.isfile(script_path):
        print("Error: scripts/setup_root_paths.py not found.")
        sys.exit(1)

    # setup_root_paths.py を実行
    # Execute setup_root_paths.py
    try:
        subprocess.run(["python3", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute setup_root_paths.py.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
