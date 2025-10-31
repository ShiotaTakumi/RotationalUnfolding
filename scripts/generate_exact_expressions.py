#!/usr/bin/env python3

import sys
from sympy import sqrt, pi, sin, cos, tan  # 記号計算 / symbolic trigonometry

# .adj ファイルから多面体の構造を読み込む関数
# Loads a polyhedron structure from an adjacency (.adj) file.
def read_adj_file(adj_path):
    num_faces = 0
    gon_list = []
    adj_edges = []
    adj_faces = []

    with open(adj_path, "r") as f:
        current_face = -1
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("NF"):
                num_faces = int(line[2:])
                gon_list = [0] * num_faces
                adj_edges = [[] for _ in range(num_faces)]
                adj_faces = [[] for _ in range(num_faces)]
            elif line.startswith("N"):
                current_face += 1
                gon_list[current_face] = int(line[1:])
            elif line.startswith("E"):
                adj_edges[current_face] = list(map(int, line[1:].split()))
            elif line.startswith("F"):
                adj_faces[current_face] = list(map(int, line[1:].split()))

    return {
        "num_faces": num_faces,
        "gon_list": gon_list,
        "adj_edges": adj_edges,
        "adj_faces": adj_faces
    }

# .ufd ファイルの 1 行を (gon, edge_id, face_id, x, y, angle) の配列に分解
# Parses one .ufd line into an array of (gon, edge_id, face_id, x, y, angle)
def parse_ufd_line(line):
    parts = line.strip().split()
    if not parts:
        return None
    face_count = int(parts[0])
    faces = []
    for i in range(face_count):
        j = 1 + i * 6
        faces.append((
            int(parts[j + 0]),  # gon
            int(parts[j + 1]),  # edge_id
            int(parts[j + 2]),  # face_id
            float(parts[j + 3]),
            float(parts[j + 4]),
            float(parts[j + 5])
        ))
    return faces

# ---- 幾何ユーティリティ / Geometry utilities ------------------------------

# 正 n 角形の内接円半径 ir = 1/(2*tan(pi/n))
# Inradius of a regular n-gon
def inradius(n):
    return 1 / (2 * tan(pi / n))

# 正 n 角形の外接円半径 cr = 1/(2*sin(pi/n))（将来的な利用に備えて定義）
# Circumradius of a regular n-gon (kept for potential future use)
def circumradius(n):
    return 1 / (2 * sin(pi / n))

# face 上で、pre_edge の位置から next_edge に至るまでの「時計回りステップ数」を数える
# Count clockwise steps on 'face_id' from 'pre_edge' to 'next_edge'
def step_count_clockwise(poly, face_id, pre_edge, next_edge):
    edges = poly["adj_edges"][face_id]
    gon = len(edges)
    # pre_edge の位置（見つからなければ 0 とする）
    try:
        pos = edges.index(pre_edge)
    except ValueError:
        pos = 0
    cnt = 1
    # C++ 実装に合わせ、(pos-1), (pos-2), ... と時計回りに辿って一致した時点の歩数を返す
    for step in range(1, gon + 1):
        idx = (pos + step) % gon
        if edges[idx] == next_edge:
            return cnt
        cnt += 1
    # 万一一致しない場合は gon を返す（理論上は起こらない想定）
    return gon

# ひとつ前の面 (prev) から次の面 (curr) の中心角 theta_center を求める
# Compute the center direction angle of the next face from the previous face
# angle_prev: 前の面の角度（ラジアン, SymPy 式）
# gon_prev  : 前の面の角数
# cnt       : 時計回りステップ数
def next_center_angle(angle_prev, gon_prev, cnt):
    return angle_prev - cnt * (2*pi/gon_prev)

# 中心座標の更新： (x_prev, y_prev) -> (x_next, y_next)
# Distance between centers is inradius(prev)+inradius(curr), direction is theta_center
def next_center_position(x_prev, y_prev, ir_prev, ir_curr, theta_center):
    delta = ir_prev + ir_curr
    x_next = x_prev + delta * cos(theta_center)
    y_next = y_prev + delta * sin(theta_center)
    return x_next, y_next

# 面の「向き」の角度（出力 angle）＝ 中心間方向から π を引いたもの（C++ 実装に一致）
# Face orientation angle to output (matches C++: next_face_angle - 180deg)
def face_orientation_from_center(theta_center):
    return theta_center - pi

# ---- メイン処理 / Main pipeline --------------------------------------------

def main():
    if len(sys.argv) != 4:
        print("Usage: generate_exact_expressions.py <input.adj> <input.ufd> <output.ufd>")
        sys.exit(1)

    adj_path = sys.argv[1]
    poly = read_adj_file(adj_path)

    ufd_path = sys.argv[2]
    out_path = sys.argv[3]

    with open(ufd_path, "r", encoding="utf-8") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:

        for raw in fin:
            if not raw.strip():
                continue
            faces = parse_ufd_line(raw)
            if faces is None or len(faces) == 0:
                continue

            # 出力（式版 .ufd）の先頭に面の個数 / Write the number of faces first (expressions file)
            fout.write(f"{len(faces)} ")

            # 併せて数値版（標準出力へ .ufd 形式）を作る
            # Also build the numeric .ufd line for stdout
            numeric_line = f"{len(faces)} "

            # 角度(rad)→度数法[-180,180] へ正規化する小関数
            # Helper to normalize radians to degrees in [-180, 180]
            def norm_deg(rad_expr):
                deg = float((rad_expr * 180 / pi).evalf())
                # [-180, 180] に収める
                deg = ((deg + 180.0) % 360.0) - 180.0
                # ちょうど整数度なら小数点を出さない / if integer, print as int-like
                if abs(deg - round(deg)) < 1e-9:
                    return f"{int(round(deg))}"
                return f"{deg:.6f}"

            # 基準面（0 番目）/ Base face (index 0)
            gon0, edge0, face0, *_ = faces[0]
            x0_expr, y0_expr = 0, 0
            ang0_expr = 0  # rad

            # 式版の書き出し / expressions out
            fout.write(f"{gon0} {edge0} {face0} {x0_expr} {y0_expr} {ang0_expr} ")
            # 数値版の追加（x,y は小数5桁、angle は度数法[-180,180]）/ numeric stdout
            numeric_line += f"{gon0} {edge0} {face0} {float(0):.5f} {float(0):.5f} {norm_deg(0)} "

            # 2 面目（1 番目）：C++ の getSecondFaceState に対応
            # Second face (index 1): corresponds to getSecondFaceState in C++
            if len(faces) >= 2:
                gon1, edge1, face1, *_ = faces[1]
                ir0 = inradius(gon0)
                ir1 = inradius(gon1)
                x1_expr = ir0 + ir1
                y1_expr = 0
                ang1_expr = -pi  # -180 deg

                # 式版
                fout.write(f"{gon1} {edge1} {face1} {x1_expr} {y1_expr} {ang1_expr} ")
                # 数値版
                x1_num = float(x1_expr.evalf())
                y1_num = float(0)
                numeric_line += f"{gon1} {edge1} {face1} {x1_num:.6f} {y1_num:.6f} {norm_deg(ang1_expr)} "

                # 3 面目以降 / From the 3rd face onward
                prev_cx_expr, prev_cy_expr, prev_ang_expr = x1_expr, y1_expr, ang1_expr
                prev_gon = gon1
                prev_face_id = face1
                prev_edge_id = edge1

                for idx in range(2, len(faces)):
                    gon_i, edge_i, face_i, *_ = faces[idx]

                    # 時計回りの辺巡回差分（step 数）/ clockwise step count on previous face
                    cnt = step_count_clockwise(poly, prev_face_id, prev_edge_id, edge_i)

                    # 中心方向角 θ_center / center direction angle
                    theta_center = next_center_angle(prev_ang_expr, prev_gon, cnt)

                    # 中心座標 (cx, cy) / center position
                    ir_prev = inradius(prev_gon)
                    ir_curr = inradius(gon_i)
                    cx_expr, cy_expr = next_center_position(prev_cx_expr, prev_cy_expr, ir_prev, ir_curr, theta_center)

                    # 面の向き（出力 angle）/ face orientation angle
                    ang_i_expr = face_orientation_from_center(theta_center)

                    # 式版
                    fout.write(f"{gon_i} {edge_i} {face_i} {cx_expr} {cy_expr} {ang_i_expr} ")

                    # 数値版
                    cx_num = float(cx_expr.evalf())
                    cy_num = float(cy_expr.evalf())
                    numeric_line += f"{gon_i} {edge_i} {face_i} {cx_num:.5f} {cy_num:.5f} {norm_deg(ang_i_expr)} "

                    # 次のループのため更新 / advance
                    prev_cx_expr, prev_cy_expr = cx_expr, cy_expr
                    prev_ang_expr = ang_i_expr
                    prev_gon = gon_i
                    prev_face_id = face_i
                    prev_edge_id = edge_i

            # 行終了 / finalize one unfolding line
            fout.write("\n")
            print(numeric_line.strip())


if __name__ == "__main__":
    main()