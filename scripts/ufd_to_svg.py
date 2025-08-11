#!/usr/bin/env python3

import os
import math

# 整面凸多面体のクラスの一覧
# List of classes of convex regular-faced polyhedra
poly_classes = ["platonic", "archimedean", "prism", "antiprism", "johnson"]


# .ufd ファイルの各行を要素ごとに分類するヘルパー関数
# Helper function to classify each element in a line of the .ufd file
def split_ufd_line(items):
    # 部分展開図における面の個数
    # Number of faces in this partial unfolding
    num_faces = int(items[0])

    # 面の辺の数（何角形か）
    # Number of edges (gon) of the face
    gon = []
    # 一つ前に展開された面と接続している辺の番号
    # Edge ID shared with the previous face
    edge_id = []
    # 面の番号 / Face ID
    face_id = []
    # 面の中心の x, y 座標
    # Face center coordinates
    x_coord, y_coord = [], []
    # 面が向いている方向（度数法）
    # Face orientation in degrees
    degree = []

    # .ufd ファイルから要素を順に取り出す
    # Sequentially extract elements from the .ufd file
    for i in range(num_faces):
        j = 1 + i * 6
        gon.append(int(items[j + 0]))
        edge_id.append(int(items[j + 1]))
        face_id.append(int(items[j + 2]))
        x_coord.append(float(items[j + 3]))
        y_coord.append(float(items[j + 4]))
        degree.append(float(items[j + 5]))

    return gon, edge_id, face_id, x_coord, y_coord, degree


# 各行を SVG として書き出す関数
# Function to write each line as an SVG file
def write_svg(output_path, gon, edge_id, face_id, x_coord, y_coord, degree,
              draw_face_labels=False, draw_edge_labels=False):
    # 描画範囲の計算に使う境界値
    # Bounds for the viewBox
    bx_min = float("inf")
    bx_max = -float("inf")
    by_min = float("inf")
    by_max = -float("inf")

    # 各面の頂点列（(x,y) の配列）
    # List of vertex lists for faces
    face_vertices = []

    # 各面の頂点計算 / compute vertices for each face
    # degree は辺の法線の向きを表すので、頂点を向くように半角ずらす
    # Degree is the direction of the edge normal; shift by half step to point to the vertex
    adjusted_degrees = []
    for i in range(len(gon)):
        rot = 360.0 / float(gon[i])  # 各辺の角度 / step angle between vertices
        d = degree[i] - rot / 2.0
        adjusted_degrees.append(d)

        # n 角形の外接円の半径 / Circumradius of the n‑gon
        radius = 1.0 / (2.0 * math.sin(math.pi / float(gon[i])))

        coords = []
        for _ in range(gon[i]):
            vx = x_coord[i] + radius * math.cos(math.pi * d / 180.0)
            vy = y_coord[i] + radius * math.sin(math.pi * d / 180.0)
            coords.append((vx, vy))
            d -= rot  # 次の頂点へ / Move to next vertex

            # 境界の更新 / Update bounds
            if vx < bx_min: bx_min = vx
            if vx > bx_max: bx_max = vx
            if vy < by_min: by_min = vy
            if vy > by_max: by_max = vy

        face_vertices.append(coords)

    # 少し余白を追加 / Add small margins
    bx_min -= 0.05
    bx_max += 0.05
    by_min -= 0.05
    by_max += 0.05
    bw = abs(bx_max - bx_min)
    bh = abs(by_max - by_min)

    # ラベル用の相対サイズを決める（ビュー領域に対して 0.2% 程度）
    # Relative font size for labels (about 0.2% of view size)
    ref = max(1e-6, min(bw, bh))
    font_scale = 0.002 * ref    # 文字サイズ
    pad = 0.02 * ref            # 背景ボックスの半径的な余白

    # SVG 書き出し
    # Write SVG
    with open(output_path, "w", encoding="utf-8") as out:
        # ヘッダ
        # Header
        out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        out.write(
            f'<svg version="1.1" id="layer_1" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'x="0px" y="0px" viewBox="{bx_min} {by_min} {bw} {bh}" '
            f'style="enable-background:new {bx_min} {by_min} {bw} {bh};" xml:space="preserve">\n'
        )
        out.write('<style type="text/css">\n')
        out.write('  .no_fill_black_stroke {fill:none; stroke:#000000; stroke-width:0.02; stroke-miterlimit:10;}\n')
        out.write('  .face_text {fill:#000000; font-family:monospace;}\n')
        out.write('  .edge_text {fill:#ff0000; font-family:monospace;}\n')
        out.write('  .edge_bg {fill:#f3f3f3; stroke:#606060; stroke-width:0.02;}\n')
        out.write('</style>\n')

        # 多角形の描画
        # Draw polygons
        for verts in face_vertices:
            pts = " ".join(f"{vx}, {vy}" for (vx, vy) in verts)
            out.write(f'<polygon class="no_fill_black_stroke" points="{pts}"/>\n')

        # 面番号の描画（中心に描画）
        # Draw face IDs at face centers
        if draw_face_labels:
            for i in range(len(gon)):
                # SVG の text はユーザ単位なので、変換で相対スケールを掛ける
                # Use a transform to scale text relative to geometry
                out.write(
                    f'<text class="face_text" text-anchor="middle" dominant-baseline="middle" '
                    f'transform="matrix({font_scale} 0 0 {font_scale} {x_coord[i]} {y_coord[i]})">{face_id[i]}</text>\n'
                )

        # 辺番号の描画（赤色で書く）
        # Draw edge IDs in red on the shared edge
        if draw_edge_labels:
            # 一つ目の面には共有している辺は無いためループから除外
            # The first face has no shared edge, so it is excluded from the loop
            for i in range(1, len(gon)):
                # 辺法線方向（degree[i]）に内接円半径だけオフセットした位置に描画
                # Place label along the edge-normal direction at inradius distance
                inradius = 1.0 / (2.0 * math.tan(math.pi / float(gon[i])))
                theta = math.pi * degree[i] / 180.0  # ラジアン / Radians
                ex = x_coord[i] + inradius * math.cos(theta)
                ey = y_coord[i] + inradius * math.sin(theta)

                # 背景矩形（視認性向上のため）
                # Small background rect for legibility
                out.write(
                    f'<rect class="edge_bg" x="{ex - pad}" y="{ey - pad}" width="{2*pad}" height="{2*pad}"/>\n'
                )
                out.write(
                    f'<text class="edge_text" text-anchor="middle" dominant-baseline="middle" '
                    f'transform="matrix({font_scale} 0 0 {font_scale} {ex} {ey})">{edge_id[i]}</text>\n'
                )

        # フッタ / Footer
        out.write('</svg>\n')


def main():
    # .ufd ファイルを保存するディレクトリの親のパスを取得
    # Get the parent path of the directory where the .ufd files are stored
    unfolding_path = input("Enter the parent path of the directory where the .ufd files are stored (e.g., ../unfolding): ").strip()
    if not os.path.isdir(unfolding_path):
        print("Error: Invalid parent path for the .ufd directories.")
        exit(1)

    # <unfolding_path> 直下の利用可能なディレクトリ一覧を表示
    # Show available subdirectories directly under <unfolding_path>
    available_dirs = sorted(
        d for d in os.listdir(unfolding_path)
        if os.path.isdir(os.path.join(unfolding_path, d))
    )
    if not available_dirs:
        print(f"Error: No subdirectories found under the {unfolding_path} directory.")
        exit(1)

    print(f"\nAvailable directories under {unfolding_path}:")
    print("  " + "  ".join(available_dirs))

    # <unfolding_path> 直下のディレクトリの選択
    # Selection of directories directly under <unfolding_path>
    ufd_category = input("Enter directory name: ").strip()
    if ufd_category not in available_dirs:
        print(f"Error: '{ufd_category}' is not found under the unfolding directory.")
        exit(1)

    # 多面体のクラスの選択
    # Select the class of the polyhedron
    print("\nSelect the class of the polyhedron:")
    print("  " + "  ".join(f"{idx}: {name}" for idx, name in enumerate(poly_classes, start=1)))
    try:
        selection = int(input("Enter polyhedron class number: "))
        if not (1 <= selection <= len(poly_classes)):
            raise ValueError
    except ValueError:
        print("Error: Invalid class number.")
        exit(1)
    poly_class = poly_classes[selection - 1]

    # 選択したクラスから、多面体を選択
    # Select a polyhedron from the chosen class
    ufd_dir = os.path.join(unfolding_path, ufd_category, poly_class)
    if not os.path.isdir(ufd_dir):
        print(f"Error: Directory not found: {ufd_dir}")
        exit(1)

    ufd_files = sorted(f[:-4] for f in os.listdir(ufd_dir) if f.endswith(".ufd"))
    if not ufd_files:
        print("Error: No .ufd files found in the selected directory.")
        exit(1)

    print(f"\nAvailable polyhedron files are:")
    print("  " + "  ".join(ufd_files))

    file = input("Enter the polyhedron file name: ").strip()
    if file not in ufd_files:
        print("Error: Invalid file name.")
        exit(1)

    ufd_path = os.path.join(ufd_dir, file + ".ufd")

    # drawing ディレクトリを取得
    # Get the drawing directory
    drawing_base = input("Enter path to drawing base directory (e.g., ../drawing): ").strip()
    if not drawing_base:
        print("Error: Drawing base directory path is empty.")
        exit(1)

    # 出力先ディレクトリを生成
    # Create the output directory
    drawing_out_dir = os.path.join(drawing_base, ufd_category, poly_class, file)
    try:
        os.makedirs(drawing_out_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create output directory: {drawing_out_dir}\n{e}")
        exit(1)

    # ラベル描画の有無を確認 / Ask whether to draw labels
    draw_faces = input("Draw face IDs at face centers? (y/n) ").strip().lower().startswith("y")
    draw_edges = input("Draw edge IDs on edges (red)? (y/n) ").strip().lower().startswith("y")

    # ゼロ埋めのために .ufd ファイルの行数を取得
    # Get the number of lines in the .ufd file for zero-padding
    with open(ufd_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f if ln.strip()]
    width = len(str(len(lines)))

    # .ufd ファイルを 1 行ずつ読み込んで SVG を描画
    # Read the .ufd file line by line and draw SVGs
    for idx, raw in enumerate(lines, start=1):
        items = raw.strip().split()
        gon, e_id, f_id, xc, yc, deg = split_ufd_line(items)
        out_svg = os.path.join(drawing_out_dir, f"{str(idx).zfill(width)}.svg")
        write_svg(out_svg, gon, e_id, f_id, xc, yc, deg, draw_face_labels=draw_faces, draw_edge_labels=draw_edges)


if __name__ == "__main__":
    main()
