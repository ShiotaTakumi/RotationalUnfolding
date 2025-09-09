#!/usr/bin/env python3

import os
import sys
import subprocess

# draw_partial_unfolding.py のラッパー用スクリプト
# Wrapper script for draw_partial_unfolding.py

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
    raw_path = ""
    noniso_path = ""
    exact_path = ""
    drawing_path = ""
    with open(ini_file) as f:
        for line in f:
            if line.startswith("raw_path"):
                raw_path = line.split("=", 1)[1].strip()
            elif line.startswith("noniso_path"):
                noniso_path = line.split("=", 1)[1].strip()
            elif line.startswith("exact_path"):
                exact_path = line.split("=", 1)[1].strip()
            elif line.startswith("drawing_path"):
                drawing_path = line.split("=", 1)[1].strip()

    if not raw_path or not noniso_path or not exact_path or not drawing_path:
        print("Error: Missing required paths in path_list.ini.")
        sys.exit(1)

    # ユーザーに描画対象を選択させる
    # Let the user choose which unfolding to draw
    print("Select which unfolding to draw:")
    print("  1: raw")
    print("  2: nonisomorphic")
    print("  3: exact")
    try:
        choice = int(input("Enter choice number: ").strip())
    except ValueError:
        print("Error: Invalid input.")
        sys.exit(1)

    if choice == 1:
        selected_ufd_path = raw_path
    elif choice == 2:
        selected_ufd_path = noniso_path
    elif choice == 3:
        selected_ufd_path = exact_path
    else:
        print("Error: Invalid choice.")
        sys.exit(1)

    # scripts/draw_partial_unfolding.py への相対パスを指定
    # （必要に応じてパスの場所を変更）
    # Specify the relative path to scripts/draw_partial_unfolding.py
    # (modify the path as needed)
    script_path = os.path.join(os.path.dirname(__file__), "../../scripts/draw_partial_unfolding.py")

    if not os.path.isfile(script_path):
        print(f"Error: draw_partial_unfolding.py not found at {script_path}")
        sys.exit(1)

    # draw_partial_unfolding.py を実行
    # Execute draw_partial_unfolding.py
    try:
        subprocess.run(["python3", script_path, selected_ufd_path, drawing_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute draw_partial_unfolding.py.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
