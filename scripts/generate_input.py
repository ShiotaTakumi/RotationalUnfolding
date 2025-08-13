#!/usr/bin/env python3

import os
import sys

# 整面凸多面体のクラスの一覧
# List of classes of convex regular-faced polyhedra
poly_classes = ["platonic", "archimedean", "prism", "antiprism", "johnson"]

def main():
    # data ディレクトリへのパスを取得
    # Get the path to the data directory
    data_path = input("Enter path to data directory (e.g., ../../data): ").strip()
    if not os.path.isdir(data_path):
        print("Error: Invalid data directory path.")
        exit(1)

    # 多面体のクラスの選択
    # Select the polyhedron class
    print("\nSelect the class of the polyhedron:")
    print("  " + "  ".join(f"{idx}: {name}" for idx, name in enumerate(poly_classes, start=1)))
    try:
        selection = int(input("Enter polyhedron class number: "))
        if not (1 <= selection <= len(poly_classes)):
            raise ValueError
    except ValueError:
        print("Error: Invalid category number.")
        exit(1)
    poly_class = poly_classes[selection - 1]

    # 選択したクラスから、多面体を選択（.adj ファイルからファイル名は取得）
    # Select a polyhedron from the chosen class (file name taken from .adj files)
    adj_dir = os.path.join(data_path, "polyhedron", poly_class, "adjacent")
    if not os.path.isdir(adj_dir):
        print(f"Error: Directory not found: {adj_dir}")
        exit(1)

    adj_files = sorted(f[:-4] for f in os.listdir(adj_dir) if f.endswith(".adj"))
    print(f"\nAvailable polyhedron files are:")
    print("  " + "  ".join(adj_files))

    file = input("Enter the polyhedron file name: ").strip()
    if file not in adj_files:
        print("Error: Invalid file name.")
        exit(1)

    # 回転展開の結果（.ufd ファイル）を保存するディレクトリの親のパスを取得
    # Get the parent directory path to save the
    # rotational unfolding results (.ufd files)
    output_path = input("Enter path for output directory (e.g., ../../unfolding): ").strip()
    if not output_path:
        print("Error: Output path is empty.")
        exit(1)

    # .ufd ファイルを保存する raw/<poly_class> ディレクトリを生成
    # Create the raw/<poly_class> directory to save the .ufd file
    raw_ufd_path = os.path.join(output_path, "raw", poly_class)
    os.makedirs(raw_ufd_path, exist_ok=True)

    # 非同型な展開図を保存する nonisomorphic/<poly_class> ディレクトリを生成
    # Create the nonisomorphic/<poly_class> directory to save the non-isomorphic unfoldings
    noniso_ufd_path = os.path.join(output_path, "nonisomorphic", poly_class)
    os.makedirs(noniso_ufd_path, exist_ok=True)

    # 厳密に重なりを持つ展開図を保存する exact/<poly_class> ディレクトリを生成
    # Create the exact/<poly_class> directory to save the exactly overlapping unfoldings
    exact_ufd_path = os.path.join(output_path, "exact", poly_class)
    os.makedirs(exact_ufd_path, exist_ok=True)

    # 描画結果（SVG ファイル）を保存する親ディレクトリのパスを取得
    # Get the parent directory path to save the drawing results (SVG files)
    drawing_parent_path = input("Enter path for drawing parent directory (e.g., ../../drawing): ").strip()
    if not drawing_parent_path:
        print("Error: Drawing parent path is empty.")
        exit(1)
    if not os.path.isdir(drawing_parent_path):
        print(f"Error: Drawing parent directory does not exist: {drawing_parent_path}")
        exit(1)

    # 選択した多面体の各種パスを生成
    # Generate the paths for the selected polyhedron
    adj_path = os.path.join(data_path, "polyhedron", poly_class, "adjacent", file + ".adj")
    base_path = os.path.join(data_path, "polyhedron", poly_class, "base", file + ".base")
    raw_path = os.path.join(raw_ufd_path, file + ".ufd")
    noniso_path = os.path.join(noniso_ufd_path, file + ".ufd")
    exact_path = os.path.join(exact_ufd_path, file + ".ufd")

    # コマンドライン引数から出力先ディレクトリを取得（指定がなければカレントディレクトリ）
    # Get the output directory from the command-line argument
    # (use the current directory if not specified)
    output_dir = sys.argv[1] if len(sys.argv) >= 2 else "."
    if not os.path.isdir(output_dir):
        print(f"Error: Output directory does not exist: {output_dir}")
        exit(1)

    # 出力先ディレクトリに設定ファイル（path_list.ini）を生成し、
    # 各パスの情報を書き込む
    # Create the configuration file (path_list.ini) in the output directory
    # and write the path information for the file
    config_path = os.path.join(output_dir, "path_list.ini")
    with open(config_path, "w") as f:
        f.write("[paths]\n")
        f.write("adj_path  = " + adj_path + "\n")
        f.write("base_path = " + base_path + "\n")
        f.write("raw_path  = " + raw_path + "\n")
        f.write("noniso_path = " + noniso_path + "\n")
        f.write("exact_path = " + exact_path + "\n")
        f.write("drawing_parent_path = " + drawing_parent_path + "\n")

    print("\nSuccess!")
    print(f"Wrote configuration to {config_path}")

if __name__ == "__main__":
    main()
