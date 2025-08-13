#!/usr/bin/env python3
import os
import sys
import subprocess

# exact_overlap_checker.py のラッパースクリプト
# Wrapper script for exact_overlap_checker.py

def main():
    # scripts/exact_overlap_checker.py への相対パスを指定
    # Specify the relative path to scripts/exact_overlap_checker.py
    script_path = os.path.join(os.path.dirname(__file__), "../../scripts/exact_overlap_checker.py")

    # カレントディレクトリにある path_list.ini を読み込む前提
    # Assume path_list.ini exists in the current directory
    ini_file = os.path.join(os.getcwd(), "path_list.ini")

    if not os.path.isfile(script_path):
        print("Error: scripts/exact_overlap_checker.py not found.")
        sys.exit(1)

    if not os.path.isfile(ini_file):
        print("Error: path_list.ini not found in current directory.")
        sys.exit(1)

    # .ini ファイルを読み込み
    # Read paths from the .ini file
    adj_path = ""
    noniso_path = ""
    exact_path = ""
    with open(ini_file) as f:
        for line in f:
            if line.startswith("adj_path"):
                adj_path = line.split("=", 1)[1].strip()
            elif line.startswith("noniso_path"):
                noniso_path = line.split("=", 1)[1].strip()
            elif line.startswith("exact_path"):
                exact_path= line.split("=", 1)[1].strip()

    if not adj_path or not noniso_path or not exact_path:
        print("Error: Missing required paths in the .ini file")
        sys.exit(1)

    # exact_overlap_checker.py を実行
    # Execute exact_overlap_checker.py
    try:
        subprocess.run(["python3", script_path, noniso_path, adj_path, exact_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute exact_overlap_checker.py.")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()