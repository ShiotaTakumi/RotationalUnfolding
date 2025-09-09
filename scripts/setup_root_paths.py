#!/usr/bin/env python3

import os

def _ask_dir(prompt):
    path = input(prompt).strip()
    if not os.path.isdir(path):
        print(f"Error: Invalid directory: {path}")
        exit(1)
    return os.path.normpath(path)

def main():
    # 多面体データファイルのルートディレクトリを尋ねる
    # Ask for the root directory of polyhedron data files
    data_root = _ask_dir("Enter the root directory of polyhedron data files (e.g., ../../polyhedron): ")

    # 展開図(.ufd)の出力先ルートディレクトリを尋ねる
    # Ask for the root directory for unfolding (.ufd) outputs
    unfolding_root = _ask_dir("Enter the root directory for unfolding (.ufd) outputs (e.g., ../../unfolding): ")

    # 描画結果(.svg)のルートディレクトリを尋ねる
    # Ask for the root directory for drawing (.svg) results
    drawing_root = _ask_dir("Enter the root directory for drawing (.svg) results (e.g., ../../drawing): ")

    # config/paths.ini を出力
    # Write config/paths.ini
    os.makedirs("config", exist_ok=True)
    ini_path = os.path.join("config", "root_paths.ini")
    with open(ini_path, "w") as f:
        f.write("[roots]\n")
        f.write(f"data_root = {data_root}\n")
        f.write(f"unfolding_root = {unfolding_root}\n")
        f.write(f"drawing_root = {drawing_root}\n")

    print("\nSuccess!")
    print(f"Wrote configuration to {ini_path}")

if __name__ == "__main__":
    main()
