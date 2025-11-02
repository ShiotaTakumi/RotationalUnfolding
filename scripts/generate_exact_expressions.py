#!/usr/bin/env python3

import sys
from sympy import S, pi, sin, cos, tan

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

# .ufd ファイルから要素を順に取り出す関数
# Function to sequentially extract elements from a .ufd file
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

# 正 n 角形の内接円の半径を返す関数
# Function to return the inradius of a regular n-gon
def inradius(n):
    return 1 / (2 * tan(pi / n))

# 面上で、pre_edge の位置から next_edge に至るまでの
# 「反時計回りでのステップ数」を数える関数
# Function to count the number of counterclockwise steps on a face
# from the position of pre_edge to that of next_edge
def step_count_counterclockwise(poly, face_id, pre_edge, next_edge):
    edges = poly["adj_edges"][face_id]
    gon = len(edges)

    # pre_edge の位置を探索する（見つからなければ -1 とする）
    # Search for the position of pre_edge (set to -1 if not found)
    try:
        pos = edges.index(pre_edge)
    except ValueError:
        pos = -1

    cnt = 1

    # (pos+1), (pos+2), ... と反時計回りに辿って
    # next_edge に一致した時点のステップ数を返す
    # Traverse counterclockwise through (pos+1), (pos+2), ...
    # and return the step count when next_edge is found
    for step in range(1, gon + 1):
        idx = (pos + step) % gon
        if edges[idx] == next_edge:
            return cnt
        cnt += 1

    # 一致しない場合は -1 を返す（理論上は起こらない想定）
    # Return -1 if no match is found (this should theoretically never happen)
    return -1

# ひとつ前の面 (prev) から次の面 (curr) の方向への角度を求める関数
# Function to compute the angle from the previous face (prev)
# to the next face (curr).
def next_center_angle(angle_prev, gon_prev, cnt):
    return angle_prev - cnt * (2 * pi / gon_prev)

# 次の面の座標の中心を計算する関数
# Function to calculate the center coordinates of the next face
def next_center_position(x_prev, y_prev, ir_prev, ir_curr, theta_center):
    delta = ir_prev + ir_curr
    x_next = x_prev + delta * cos(theta_center)
    y_next = y_prev + delta * sin(theta_center)
    return x_next, y_next

# 角度 (rad) を度数法 [-180,180] で正規化するデバック用の関数
# Function to normalize an angle (in radians) to
# degrees within the range [-180, 180] for debugging purposes
def norm_deg(rad_expr):
    # ラジアン単位の SymPy 式 rad_expr を度数法に変換し、
    # さらに数値（float）として取り出す
    deg = float((rad_expr * 180 / pi).evalf())

    # [-180, 180] に収める
    deg = ((deg + 180.0) % 360.0) - 180.0

    # 小数点以下 6 桁を出力
    return f"{deg:.6f}"

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

        # 1 行ずつ取り出す
        # Read the file line by line
        for raw in fin:
            if not raw.strip():
                continue
            faces = parse_ufd_line(raw)
            if faces is None or len(faces) == 0:
                continue

            # 出力の先頭に面の個数を書く
            # Write the number of faces at the beginning of the output
            fout.write(f"{len(faces)} ")

            # [デバック] 標準出力用
            # [Debug] For standard output
            numeric_line = f"{len(faces)} "

            # 基準面（1つ目の面）
            # Base face (the first face)
            gon0, edge0, face0, *_ = faces[0]
            x0_expr, y0_expr = S.Zero, S.Zero
            ang0_expr = S.Zero

            # 式の書き出し
            # Write the symbolic expressions
            fout.write(f"{gon0} {edge0} {face0} {x0_expr} {y0_expr} {ang0_expr} ")

            # [デバック] 小数点以下 6 桁で出力
            # [Debug] Output with six decimal places
            numeric_line += f"{gon0} {edge0} {face0} {float(x0_expr):.5f} {float(y0_expr):.5f} {norm_deg(ang0_expr)} "

            if len(faces) >= 2:
                # 2つ目の面の座標と角度の計算
                # Calculate the coordinates and angle of the second face
                gon1, edge1, face1, *_ = faces[1]
                ir0 = inradius(gon0)
                ir1 = inradius(gon1)
                x1_expr = ir0 + ir1
                y1_expr = S.Zero
                ang1_expr = ang0_expr - pi

                # 式の書き出し
                # Write the symbolic expressions
                fout.write(f"{gon1} {edge1} {face1} {x1_expr} {y1_expr} {ang1_expr} ")

                # [デバック] 小数点以下 6 桁で出力
                # [Debug] Output with six decimal places
                x1_num = float(x1_expr.evalf())
                y1_num = float(y1_expr.evalf())
                numeric_line += f"{gon1} {edge1} {face1} {x1_num:.6f} {y1_num:.6f} {norm_deg(ang1_expr)} "

                # 次の面を計算するために、現在の面の状態を保持する
                # Store the current face state for calculating the next face
                prev_gon = gon1
                prev_face_id = face1
                prev_edge_id = edge1
                prev_cx_expr, prev_cy_expr, prev_ang_expr = x1_expr, y1_expr, ang1_expr

                # 3つ目以降の面の座標と角度の計算
                # Calculate the coordinates and
                # angles of the third and subsequent faces
                for idx in range(2, len(faces)):
                    gon_i, edge_i, face_i, *_ = faces[idx]

                    # pre_edge から edge_i までのステップ数（反時計回りにカウント）
                    # Step count from pre_edge to edge_i (counted counterclockwise)
                    cnt = step_count_counterclockwise(poly, prev_face_id, prev_edge_id, edge_i)

                    # 次の面の中心方向への角度
                    # Angle toward the center direction of the next face
                    theta_center = next_center_angle(prev_ang_expr, prev_gon, cnt)

                    # 次の面の中心座標
                    # Center coordinates of the next face
                    ir_prev = inradius(prev_gon)
                    ir_curr = inradius(gon_i)
                    cx_expr, cy_expr = next_center_position(prev_cx_expr, prev_cy_expr, ir_prev, ir_curr, theta_center)

                    # 次の面の向きの角度
                    # Orientation angle of the next face
                    ang_i_expr = theta_center - pi

                    # 式の書き出し
                    # Write the symbolic expressions
                    fout.write(f"{gon_i} {edge_i} {face_i} {cx_expr} {cy_expr} {ang_i_expr} ")

                    # [デバック] 小数点以下 6 桁で出力
                    # [Debug] Output with six decimal places
                    cx_num = float(cx_expr.evalf())
                    cy_num = float(cy_expr.evalf())
                    numeric_line += f"{gon_i} {edge_i} {face_i} {cx_num:.5f} {cy_num:.5f} {norm_deg(ang_i_expr)} "

                    # 次の面の式を取得するための更新
                    # Update to obtain the expressions for the next face
                    prev_cx_expr, prev_cy_expr = cx_expr, cy_expr
                    prev_ang_expr = ang_i_expr
                    prev_gon = gon_i
                    prev_face_id = face_i
                    prev_edge_id = edge_i

            # 行の読み込みの終了にともなう改行
            # Newline at the end of processing each line
            fout.write("\n")

            # デバック用の出力
            # Debug output
            print(numeric_line.strip())


if __name__ == "__main__":
    main()