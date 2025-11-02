#!/usr/bin/env python3

import os
import sys

# 整面凸多面体のクラスの一覧
# List of classes of convex regular-faced polyhedra
poly_classes = ["platonic", "archimedean", "prism", "antiprism", "johnson"]

def read_roots():
    # config/root_paths.ini からルートパスを読む
    # Read root paths from config/root_paths.ini
    ini = os.path.join("config", "root_paths.ini")
    if not os.path.isfile(ini):
        print("Error: config/root_paths.ini not found.")
        exit(1)

    data_root = unfolding_root = drawing_root = ""
    with open(ini) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("#",";","[")):
                continue
            if line.startswith("data_root"):
                data_root = line.split("=",1)[1].strip()
            elif line.startswith("unfolding_root"):
                unfolding_root = line.split("=",1)[1].strip()
            elif line.startswith("drawing_root"):
                drawing_root = line.split("=",1)[1].strip()

    if not data_root or not unfolding_root or not drawing_root:
        print("Error: Missing data_root/unfolding_root/drawing_root in config/root_paths.ini")
        exit(1)

    return data_root, unfolding_root, drawing_root

def main():
    # ルートパス読込（環境設定）
    # Load root paths (environment settings)
    data_root, unfolding_root, drawing_root = read_roots()

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
    adj_dir = os.path.join(data_root, poly_class, "adjacent")
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

    # 展開図(.ufd)を保存する raw/nonisomorphic/expr/exact の各ディレクトリを生成
    # Create raw / nonisomorphic / exact directories to save .ufd files
    raw_ufd_path     = os.path.join(unfolding_root, "raw",           poly_class)
    noniso_ufd_path  = os.path.join(unfolding_root, "nonisomorphic", poly_class)
    expr_ufd_path    = os.path.join(unfolding_root, "expression",    poly_class)
    exact_ufd_path   = os.path.join(unfolding_root, "exact",         poly_class)
    os.makedirs(raw_ufd_path,    exist_ok=True)
    os.makedirs(noniso_ufd_path, exist_ok=True)
    os.makedirs(exact_ufd_path,  exist_ok=True)

    # 選択した多面体の各種パスを生成
    # Generate the paths for the selected polyhedron
    adj_path    = os.path.join(data_root, poly_class, "adjacent", file + ".adj")
    base_path   = os.path.join(data_root, poly_class, "base",     file + ".base")
    raw_path    = os.path.join(raw_ufd_path,    file + ".ufd")
    noniso_path = os.path.join(noniso_ufd_path, file + ".ufd")
    expr_path   = os.path.join( expr_ufd_path,  file + ".ufd")
    exact_path  = os.path.join(exact_ufd_path,  file + ".ufd")

    # 出力先ディレクトリ（指定がなければカレント）に path_list.ini を出力
    # Write path_list.ini to the output directory (current dir by default)
    output_dir = sys.argv[1] if len(sys.argv) >= 2 else "."
    if not os.path.isdir(output_dir):
        print(f"Error: Output directory does not exist: {output_dir}")
        exit(1)

    config_path = os.path.join(output_dir, "config/path_lists.ini")
    with open(config_path, "w") as f:
        f.write("[paths]\n")
        f.write("adj_path  = " + adj_path + "\n")
        f.write("base_path = " + base_path + "\n")
        f.write("raw_path  = " + raw_path + "\n")
        f.write("noniso_path = " + noniso_path + "\n")
        f.write("expr_path = " + expr_path + "\n")
        f.write("exact_path = " + exact_path + "\n")
        f.write("drawing_path = " + drawing_root + "\n")

    print("\nSuccess!")
    print(f"Wrote configuration to {config_path}")

if __name__ == "__main__":
    main()
