#!/usr/bin/env python3
import os
import sys
import subprocess

# ufd_to_svg.py のラッパースクリプト
# Wrapper script for ufd_to_svg.py

def main():
    # scripts/ufd_to_svg.py への相対パスを指定
    # Specify the relative path to scripts/ufd_to_svg.py
    script_path = os.path.join(os.path.dirname(__file__), "../../scripts/ufd_to_svg.py")

    # カレントディレクトリにある path_list.ini を読み込む前提
    # Assume path_list.ini exists in the current directory
    ini_file = os.path.join(os.getcwd(), "path_list.ini")

    if not os.path.isfile(script_path):
        print("Error: scripts/ufd_to_svg.py not found.")
        sys.exit(1)

    if not os.path.isfile(ini_file):
        print("Error: path_list.ini not found in current directory.")
        sys.exit(1)

    # .ini ファイルを読み込み
    # Read paths from the .ini file
    noniso_path = ""
    drawing_parent_path = ""
    with open(ini_file) as f:
        for line in f:
            if line.startswith("noniso_path"):
                noniso_path = line.split("=", 1)[1].strip()
            elif line.startswith("drawing_parent_path"):
                drawing_parent_path = line.split("=", 1)[1].strip()

    if not noniso_path or not drawing_parent_path:
        print("Error: Missing 'noniso_path' or 'drawing_parent_path' in path_list.ini.")
        sys.exit(1)

    # ufd_to_svg.py を実行
    # Execute ufd_to_svg.py
    try:
        subprocess.run(["python3", script_path, noniso_path, drawing_parent_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute ufd_to_svg.py.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
