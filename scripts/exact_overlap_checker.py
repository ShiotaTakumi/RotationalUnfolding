#!/usr/bin/env python3

import sys
from sympy import sympify, pi, sin, cos

# .adj ファイルから多面体の構造を読み込む関数
# Loads a polyhedron structure from an adjacency (.adj) file.
def read_adj_file(adj_path):
    num_faces = 0
    gon_list = []
    vertices = []
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
                vertices  = [[] for _ in range(num_faces)]
                adj_edges = [[] for _ in range(num_faces)]
                adj_faces = [[] for _ in range(num_faces)]
            elif line.startswith("N"):
                current_face += 1
                gon_list[current_face] = int(line[1:])
            elif line.startswith("V"):
                vertices[current_face] = list(map(int, line[1:].split()))
            elif line.startswith("E"):
                adj_edges[current_face] = list(map(int, line[1:].split()))
            elif line.startswith("F"):
                adj_faces[current_face] = list(map(int, line[1:].split()))

    return {
        "num_faces": num_faces,
        "gon_list": gon_list,
        "vertices": vertices,
        "adj_edges": adj_edges,
        "adj_faces": adj_faces
    }

# 正 n 角形の外接円半径を返す関数
def circumradius(n):
    return 1 / (2 * sin(pi / n))

# 1 面の中心座標 (cx, cy) と角度 ang から頂点列を生成する関数
def get_vertices_of_face(gon, cx, cy, ang):
    r = circumradius(gon)
    offset = pi / gon  # 半辺ぶんの回転オフセット
    vertices = []
    for k in range(gon):
        theta = ang + offset + 2 * pi * k / gon
        xk = cx + r * cos(theta)
        yk = cy + r * sin(theta)
        vertices.append((xk, yk))
    return vertices

# .ufd ファイルから要素を順に取り出す関数（記号式対応）
def parse_ufd_line_symbolic(line):
    parts = line.strip().split()
    if not parts:
        return None
    face_count = int(parts[0])
    faces = []
    for i in range(face_count):
        j = 1 + i * 6
        faces.append((
            int(parts[j + 0]),              # gon
            int(parts[j + 1]),              # edge_id
            int(parts[j + 2]),              # face_id
            sympify(parts[j + 3]),          # x (symbolic)
            sympify(parts[j + 4]),          # y (symbolic)
            sympify(parts[j + 5])           # angle (symbolic, rad)
        ))
    return faces

# --- 追加ユーティリティ ------------------------------------------------------

def shares_vertex(poly, face_id_a, face_id_b):
    """adj の V 行に基づき、2 面が共有頂点を持つかを判定"""
    va = set(poly["vertices"][face_id_a])
    vb = set(poly["vertices"][face_id_b])
    return len(va & vb) > 0

def enumerate_candidate_pairs(poly, faces):
    """
    Mathematica 版の pairs 構築ロジックを Python で再現。
    i と i+1 の共有頂点集合を保ちながら前方へ辿り、
    共有連鎖が途切れた以降の j を候補に加える（(0, 最後) は除外）。
    """
    face_ids = [fi for (_, _, fi, *_) in faces]
    V = poly["vertices"]
    n = len(face_ids)
    pairs = set()

    for i in range(n - 1):
        shared = set(V[face_ids[i]]) & set(V[face_ids[i + 1]])
        flag = True  # True の間は共有頂点連鎖を追跡中

        for j in range(i + 2, n):  # 直近の隣 (i+1) は除外
            if flag:
                v = shared & set(V[face_ids[j]])
                if v:
                    # まだ連鎖中：スキップしつつ shared を更新して継続
                    shared = v
                    continue
                else:
                    # ここで連鎖が途切れた → ここから先は候補
                    flag = False

            # (0, 最後) は先に個別チェックするので除外
            if not (i == 0 and j == n - 1):
                pairs.add((i, j))

    return sorted(pairs)

def polygons_overlap(poly1, poly2):
    # TODO: 後で exact 判定をここに実装
    return False

def main():
    if len(sys.argv) != 4:
        print("Usage: exact_overlap_checker.py <input.adj> <input.ufd> <output.ufd>")
        sys.exit(1)

    adj_path = sys.argv[1]
    poly = read_adj_file(adj_path)

    ufd_path = sys.argv[2]
    out_path = sys.argv[3]

    with open(ufd_path, "r", encoding="utf-8") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:

        partial_count = 0  # ← カウンタ追加

        for raw in fin:
            if not raw.strip():
                continue
            faces = parse_ufd_line_symbolic(raw)
            if faces is None:
                continue

            partial_count += 1
            print(f"\nPartial unfolding: {partial_count}\n")  # ← ここで出力

            polygons = []
            # 各面の頂点列を計算して表示（最後の行にはカンマを付けない）
            for idx, (gon, _, face_id, cx, cy, ang) in enumerate(faces):
                vertices = get_vertices_of_face(gon, cx, cy, ang)
                polygons.append((face_id, vertices))
                # デバッグ（下のコードを実行する）
                """
                Graphics[
                 {
                  EdgeForm[Black],
                  FaceForm[LightBlue],
                  Map[ScalingTransform[{1, -1}], {
                  (*ここに、コピーする*)
                  }]
                 },
                 Axes -> True,
                 AspectRatio -> Automatic
                ]
                """
                # coords = ", ".join([f"{{{xk.evalf():.5f}, {yk.evalf():.5f}}}" for xk, yk in vertices])
                # comma = "," if idx < len(faces) - 1 else ""  # 最後の要素以外にはカンマ
                # nline = "" if idx < len(faces) - 1 else "\n"  # 最後の行は改行
                # print(f"Polygon[{{{coords}}}]{comma}  (* face {face_id} *) {nline}")

            # --- 隣接していない全ての面の組み合わせをチェック ---
            num_faces = len(polygons)
            for i in range(num_faces):
                for j in range(i + 1, num_faces):
                    id1, poly1 = polygons[i]
                    id2, poly2 = polygons[j]

                    # TODO: 元から隣接してる面の組みは除外

                    overlap = polygons_overlap(poly1, poly2)
                    fout.write(f"{id1} {id2} {overlap}\n")  # 出力ファイルに結果を書き出す

                    # [デバッグ出力]
                    print(f"Check faces ({id1}, {id2}) → {overlap}")

            print('\n')

if __name__ == "__main__":
    main()
