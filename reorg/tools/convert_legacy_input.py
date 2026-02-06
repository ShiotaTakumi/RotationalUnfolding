#!/usr/bin/env python3
# ============================================================================
# convert_legacy_input.py
# ============================================================================
#
# What this script does:
#   Converts legacy .adj and .base files to the new JSON format
#   (polyhedron.json and root_pairs.json).
#
# このスクリプトの役割:
#   legacy の .adj および .base ファイルを新しい JSON 形式
#   （polyhedron.json および root_pairs.json）に変換する。
#
# Usage:
#   python3 convert_legacy_input.py <adj_file> <base_file> <output_dir>
#
# 使用方法:
#   python3 convert_legacy_input.py <adjファイル> <baseファイル> <出力ディレクトリ>
#
# Output:
#   - <output_dir>/polyhedron.json (pretty-printed)
#   - <output_dir>/root_pairs.json (pretty-printed)
#
# 出力:
#   - <出力ディレクトリ>/polyhedron.json (整形済み)
#   - <出力ディレクトリ>/root_pairs.json (整形済み)
#
# ============================================================================

import json
import os
import sys


def read_adj_file(adj_path):
    """
    Reads a legacy .adj file and returns a structured dictionary.

    legacy の .adj ファイルを読み込み、構造化された辞書を返す。

    Returns:
        {
            "num_faces": int,
            "faces": [
                {
                    "face_id": int,
                    "gon": int,
                    "vertices": [int, ...],
                    "edges": [int, ...],
                    "adjacent_faces": [int, ...]
                },
                ...
            ]
        }
    """
    num_faces = 0
    faces = []

    with open(adj_path, "r", encoding="utf-8") as f:
        current_face = None
        current_face_id = -1

        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            # 空行とコメントをスキップ
            if not line or line.startswith("#"):
                continue

            if line.startswith("NF"):
                num_faces = int(line[2:].strip())
            elif line.startswith("N"):
                current_face_id += 1
                gon = int(line[1:].strip())
                current_face = {
                    "face_id": current_face_id,
                    "gon": gon,
                    "vertices": [],
                    "edges": [],
                    "adjacent_faces": []
                }
                faces.append(current_face)
            elif line.startswith("V"):
                vertices = list(map(int, line[1:].strip().split()))
                current_face["vertices"] = vertices
            elif line.startswith("E"):
                edges = list(map(int, line[1:].strip().split()))
                current_face["edges"] = edges
            elif line.startswith("F"):
                adjacent_faces = list(map(int, line[1:].strip().split()))
                current_face["adjacent_faces"] = adjacent_faces

    return {
        "num_faces": num_faces,
        "faces": faces
    }


def read_base_file(base_path):
    """
    Reads a legacy .base file and returns a list of (face, edge) pairs.

    legacy の .base ファイルを読み込み、(面, 辺) ペアのリストを返す。

    Returns:
        [(base_face, base_edge), ...]
    """
    root_pairs = []

    with open(base_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                face = int(parts[0])
                edge = int(parts[1])
                root_pairs.append((face, edge))

    return root_pairs


def extract_poly_info(adj_path):
    """
    Extracts polyhedron class and name from the .adj file path.

    .adj ファイルパスから多面体のクラスと名前を抽出する。

    Example:
        Input:  ../polyhedron/archimedean/adjacent/s05.adj
        Output: ("archimedean", "s05")

    例:
        入力:  ../polyhedron/archimedean/adjacent/s05.adj
        出力: ("archimedean", "s05")
    """
    # Normalize path and split into components
    # パスを正規化してコンポーネントに分割
    norm_path = os.path.normpath(adj_path)
    parts = norm_path.split(os.sep)

    # Extract filename without extension
    # 拡張子を除いたファイル名を抽出
    filename = os.path.basename(adj_path)
    poly_name = os.path.splitext(filename)[0]

    # Try to find the class name (directory before "adjacent")
    # クラス名を探す（"adjacent" の前のディレクトリ）
    poly_class = "unknown"
    for i, part in enumerate(parts):
        if part == "adjacent" and i > 0:
            poly_class = parts[i - 1]
            break

    return poly_class, poly_name


def create_polyhedron_json(adj_data, poly_class, poly_name):
    """
    Creates the polyhedron.json structure from parsed .adj data.

    解析された .adj データから polyhedron.json 構造を作成する。
    """
    faces_list = []

    for face in adj_data["faces"]:
        # Build neighbors array from edges and adjacent_faces
        # edges と adjacent_faces から neighbors 配列を構築
        neighbors = []
        for edge_id, adj_face_id in zip(face["edges"], face["adjacent_faces"]):
            neighbors.append({
                "edge_id": edge_id,
                "face_id": adj_face_id
            })

        faces_list.append({
            "face_id": face["face_id"],
            "gon": face["gon"],
            "neighbors": neighbors
        })

    return {
        "schema_version": 1,
        "polyhedron": {
            "class": poly_class,
            "name": poly_name
        },
        "faces": faces_list
    }


def create_root_pairs_json(root_pairs):
    """
    Creates the root_pairs.json structure from parsed .base data.

    解析された .base データから root_pairs.json 構造を作成する。
    """
    pairs_list = []
    for face, edge in root_pairs:
        pairs_list.append({
            "base_face": face,
            "base_edge": edge
        })

    return {
        "schema_version": 1,
        "root_pairs": pairs_list
    }


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 convert_legacy_input.py <adj_file> <base_file> <output_dir>")
        print("")
        print("Example:")
        print("  python3 convert_legacy_input.py \\")
        print("    polyhedron/archimedean/adjacent/s05.adj \\")
        print("    polyhedron/archimedean/base/s05.base \\")
        print("    data/polyhedra/archimedean/s05")
        sys.exit(1)

    adj_path = sys.argv[1]
    base_path = sys.argv[2]
    output_dir = sys.argv[3]

    # Check input files exist
    # 入力ファイルが存在することを確認
    if not os.path.isfile(adj_path):
        print(f"Error: .adj file not found: {adj_path}")
        sys.exit(1)
    if not os.path.isfile(base_path):
        print(f"Error: .base file not found: {base_path}")
        sys.exit(1)

    # Create output directory
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)

    # Parse input files
    # 入力ファイルを解析
    print(f"Reading {adj_path}...")
    adj_data = read_adj_file(adj_path)

    print(f"Reading {base_path}...")
    root_pairs = read_base_file(base_path)

    # Extract polyhedron class and name
    # 多面体のクラスと名前を抽出
    poly_class, poly_name = extract_poly_info(adj_path)
    print(f"Detected: class={poly_class}, name={poly_name}")

    # Create JSON structures
    # JSON 構造を作成
    polyhedron_json = create_polyhedron_json(adj_data, poly_class, poly_name)
    root_pairs_json = create_root_pairs_json(root_pairs)

    # Write JSON files (pretty-printed with indent=2)
    # JSON ファイルを書き込み（インデント2で整形）
    polyhedron_path = os.path.join(output_dir, "polyhedron.json")
    root_pairs_path = os.path.join(output_dir, "root_pairs.json")

    print(f"Writing {polyhedron_path}...")
    with open(polyhedron_path, "w", encoding="utf-8") as f:
        json.dump(polyhedron_json, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add trailing newline

    print(f"Writing {root_pairs_path}...")
    with open(root_pairs_path, "w", encoding="utf-8") as f:
        json.dump(root_pairs_json, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add trailing newline

    print(f"\nSuccess! Converted:")
    print(f"  {adj_path} + {base_path}")
    print(f"  -> {polyhedron_path}")
    print(f"  -> {root_pairs_path}")
    print(f"\nFaces: {adj_data['num_faces']}, Root pairs: {len(root_pairs)}")


if __name__ == "__main__":
    main()
