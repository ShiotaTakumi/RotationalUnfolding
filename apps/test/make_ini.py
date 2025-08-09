#!/usr/bin/env python3

# generate_input.py のラッパー用スクリプト
# Wrapper script for generate_input.py

import subprocess
import os
import sys

def main():
    # scripts/generate_input.py への相対パスを
    # script_path に指定する（必要に応じてパスの場所を変更）
    # Specify the relative path to scripts/generate_input.py
    # as script_path (modify the path as needed)
    script_path = os.path.join(os.path.dirname(__file__), "../../scripts/generate_input.py")

    # カレントディレクトリを設定ファイル（.ini）の出力先として指定
    # Set the current directory as the output destination for the configuration (.ini) file
    output_dir = os.getcwd()

    # scripts/generate_input.py が存在するか確認
    # Check if scripts/generate_input.py exists
    if not os.path.isfile(script_path):
        print("Error: scripts/generate_input.py not found.")
        sys.exit(1)

    # generate_input.py を実行（第 1 引数に出力先ディレクトリを渡す）
    # Execute generate_input.py (pass the output directory as the first argument)
    try:
        subprocess.run(["python3", script_path, output_dir], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute generate_input.py.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
