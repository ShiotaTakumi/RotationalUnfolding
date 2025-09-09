#!/usr/bin/env python3

import subprocess
import os
import sys

# generate_path_lists.py のラッパー用スクリプト
# Wrapper script for generate_path_lists.py

def main():
    # scripts/generate_path_lists.py への相対パスを指定
    # （必要に応じてパスの場所を変更）
    # Specify the relative path to scripts/generate_path_lists.py
    # (modify the path as needed)
    script_path = os.path.join(os.path.dirname(__file__), "../scripts/generate_path_lists.py")

    if not os.path.isfile(script_path):
        print("Error: scripts/generate_path_lists.py not found.")
        sys.exit(1)

    # generate_path_lists.py を実行
    # Execute generate_path_lists.py
    try:
        subprocess.run(["python3", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute generate_path_lists.py.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
