#!/usr/bin/env python3

import os
import sys
import math

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
def write_svg(output_path, gon, edge_id, face_id, x_coord, y_coord, degree):
    # 描画範囲の計算に使う境界値
    # Bounds for the viewBox
    bx_min = float("inf")
    bx_max = -float("inf")
    by_min = float("inf")
    by_max = -float("inf")

    # 各面の頂点列（(x,y) の配列）
    # List of vertex lists for faces
    face_vertices = []

    # 各面の頂点計算
    # Compute vertices for each face
    adjusted_degrees = []
    for i in range(len(gon)):
        # 各辺の角度 / step angle between vertices
        rot = 360.0 / float(gon[i])

        # degree は辺の法線の向きを表すので、頂点を向くように半角ずらす
        # Degree is the direction of the edge normal;
        # shift by half step to point to the vertex
        d = degree[i] - rot / 2.0
        adjusted_degrees.append(d)

        # n 角形の外接円の半径
        # Circumradius of the n‑gon
        radius = 1.0 / (2.0 * math.sin(math.pi / float(gon[i])))

        coords = []
        for _ in range(gon[i]):
            vx = x_coord[i] + radius * math.cos(math.pi * d / 180.0)
            vy = y_coord[i] + radius * math.sin(math.pi * d / 180.0)
            coords.append((vx, vy))
            # 次の頂点へ / Move to next vertex
            d -= rot

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

    # SVG 書き出し / Write SVG
    with open(output_path, "w", encoding="utf-8") as out:
        # ヘッダ / Header
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

        # 多角形の描画 / Draw polygons
        for verts in face_vertices:
            pts = " ".join(f"{vx}, {vy}" for (vx, vy) in verts)
            out.write(f'<polygon class="no_fill_black_stroke" points="{pts}"/>\n')

        # 面番号の描画（中心に描画）/ Draw face IDs at face centers
        for i in range(len(gon)):
            # SVG の text はユーザ単位なので、変換で相対スケールを掛ける
            # Use a transform to scale text relative to geometry
            out.write(
                f'<text class="face_text" text-anchor="middle" dominant-baseline="middle" '
                f'transform="matrix({font_scale} 0 0 {font_scale} {x_coord[i]} {y_coord[i]})">{face_id[i]}</text>\n'
            )

        # 辺番号の描画（赤色で書く）
        # 一つ目の面には共有している辺は無いためループから除外
        # Draw edge IDs in red on the shared edge
        # The first face has no shared edge, so it is excluded from the loop
        for i in range(1, len(gon)):
            # 辺法線方向（degree[i]）に内接円半径だけオフセットした位置に描画
            # Place label along the edge-normal direction at inradius distance
            inradius = 1.0 / (2.0 * math.tan(math.pi / float(gon[i])))
            theta = math.pi * degree[i] / 180.0  # ラジアン / Radians
            ex = x_coord[i] + inradius * math.cos(theta)
            ey = y_coord[i] + inradius * math.sin(theta)

            # 辺の上に矩形を描く（辺番号の視認性向上のため）
            # Draw a rectangle on the edge (to improve the visibility of the edge number)
            out.write(
                f'<rect class="edge_bg" x="{ex - pad}" y="{ey - pad}" width="{2*pad}" height="{2*pad}"/>\n'
            )
            out.write(
                f'<text class="edge_text" text-anchor="middle" dominant-baseline="middle" '
                f'transform="matrix({font_scale} 0 0 {font_scale} {ex} {ey})">{edge_id[i]}</text>\n'
            )

        # フッタ / Footer
        out.write('</svg>\n')


def build_output_dir_path(ufd_path, drawing_base):
    # .ufd の絶対パスを取得 / Get absolute path to the .ufd
    ufd_abs = os.path.abspath(ufd_path)

    # ディレクトリ部分を階層ごとに分割 / Split the directory part into components
    parts = os.path.normpath(os.path.dirname(ufd_abs)).split(os.sep)

    # 末尾2階層を category / poly_class とみなす（不足時は 'unknown' を補う）
    # Treat the last two directories as category / poly_class (fallback to 'unknown' if missing)
    poly_class = parts[-1] if len(parts) >= 1 else "unknown"
    category   = parts[-2] if len(parts) >= 2 else "unknown"

    # 拡張子を除いたファイル名を取得 / Get filename without extension
    file_stem = os.path.splitext(os.path.basename(ufd_abs))[0]

    # 出力先パスを組み立てる：<drawing_base>/<category>/<poly_class>/<file_stem>/
    # Build output path: <drawing_base>/<category>/<poly_class>/<file_stem>/
    return os.path.join(os.path.abspath(drawing_base), category, poly_class, file_stem)


def main():
    if len(sys.argv) != 3:
        print("Usage: ufd_to_svg.py <ufd_path> <drawing_base_dir>")
        sys.exit(1)

    ufd_path = sys.argv[1]
    drawing_base = sys.argv[2]

    if not os.path.isfile(ufd_path):
        print(f"Error: .ufd file not found: {ufd_path}")
        sys.exit(1)

    # 出力先ディレクトリを構築して生成
    # Build and create the output directory
    drawing_out_dir = build_output_dir_path(ufd_path, drawing_base)
    try:
        os.makedirs(drawing_out_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create output directory: {drawing_out_dir}\n{e}")
        sys.exit(1)

    # .ufd ファイルから行を読み込む
    # Read lines from the .ufd file
    with open(ufd_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f if ln.strip()]

    if not lines:
        print(f"Error: .ufd file is empty: {ufd_path}")
        sys.exit(1)

    # ゼロ埋め幅を計算 / Compute zero-padding width
    width = len(str(len(lines)))

    # .ufd ファイルを 1 行ずつ読み込んで SVG を描画
    # Read the .ufd file line by line and draw SVGs
    count = 0
    for idx, raw in enumerate(lines, start=1):
        items = raw.strip().split()
        gon, e_id, f_id, xc, yc, deg = split_ufd_line(items)
        out_svg = os.path.join(drawing_out_dir, f"{str(idx).zfill(width)}.svg")
        write_svg(out_svg, gon, e_id, f_id, xc, yc, deg)
        count += 1

    print(f"Done. Wrote {count} SVG files to: {drawing_out_dir}")


if __name__ == "__main__":
    main()
