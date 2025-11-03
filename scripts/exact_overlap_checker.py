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

# 2 面 (i, j) とその「間」にあるすべての面が共有する頂点が1つ以上あるかを判定
# （＝連鎖がずっと続いているか。続いているならペアを除外）
def shares_vertex_chain_all(poly, faces, i, j):
    face_ids = [fi for (_, _, fi, *_) in faces]
    V = poly["vertices"]
    common = set(V[face_ids[i]])
    for t in range(i + 1, j + 1):
        common &= set(V[face_ids[t]])
        if not common:
            return False
    return len(common) > 0

def polygons_overlap(poly1, poly2):
    """
    Mathematica版と同値の意味論（交差／端点接触／同一直線上の重なりを True）。
    ハイブリッド実装：
      1) 高精度 evalf による数値判定（高速）
      2) 数値的に不安定（符号が不確実/ほぼ共線/端点・辺にほぼ載る）なら
         SymPy の厳密幾何 Segment.intersection() にフォールバック（完全厳密）
    """
    from sympy import sympify, Abs
    from sympy.geometry import Point, Segment

    # --- 数値フェーズの設定 ---------------------------------------------------
    prec_fast = 80                 # 数値段階の作業桁（必要に応じて 60〜100 で調整）
    eps      = sympify('1e-30')    # 外積・投影のしきい値（prec_fast に見合う絶対閾）

    def _num(x):
        return sympify(x).evalf(prec_fast)

    # (* Polygon の頂点列から辺リストを作る：最後と最初も結ぶ *)
    def edges_of(poly):
        verts = poly
        m = len(verts)
        return [(verts[i], verts[(i + 1) % m]) for i in range(m)]

    # AABB の高速除外（数値）
    def aabb_overlap(a1, a2, b1, b2):
        ax1, ay1 = _num(a1[0]), _num(a1[1]); ax2, ay2 = _num(a2[0]), _num(a2[1])
        bx1, by1 = _num(b1[0]), _num(b1[1]); bx2, by2 = _num(b2[0]), _num(b2[1])
        minAx, maxAx = min(ax1, ax2), max(ax1, ax2)
        minAy, maxAy = min(ay1, ay2), max(ay1, ay2)
        minBx, maxBx = min(bx1, bx2), max(bx1, bx2)
        minBy, maxBy = min(by1, by2), max(by1, by2)
        # !(maxA < minB || maxB < minA) を eps マージンつきで
        return not (
            (maxAx < minBx - eps) or
            (maxBx < minAx - eps) or
            (maxAy < minBy - eps) or
            (maxBy < minAy - eps)
        )

    # 外積（有向面積×2）
    def orient(a, b, c):
        ax, ay = _num(a[0]), _num(a[1])
        bx, by = _num(b[0]), _num(b[1])
        cx, cy = _num(c[0]), _num(c[1])
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    # 点 p が線分 ab 上（数値）かどうか：共線＆射影が区間内
    def on_segment_num(p, a, b):
        ax, ay = _num(a[0]), _num(a[1])
        bx, by = _num(b[0]), _num(b[1])
        px, py = _num(p[0]), _num(p[1])

        cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
        if Abs(cross) > eps:
            return False

        dot  = (px - ax) * (bx - ax) + (py - ay) * (by - ay)
        seg2 = (bx - ax) * (bx - ax) + (by - ay) * (by - ay)
        if dot < -eps or dot > seg2 + eps:
            return False
        return True

    # --- ここから辺ペアの走査（数値 → 必要時に厳密）--------------------------
    edges1 = edges_of(poly1)
    edges2 = edges_of(poly2)

    for (a1, a2) in edges1:
        for (b1, b2) in edges2:
            if not aabb_overlap(a1, a2, b1, b2):
                continue

            d1 = orient(a1, a2, b1)
            d2 = orient(a1, a2, b2)
            d3 = orient(b1, b2, a1)
            d4 = orient(b1, b2, a2)

            if (d1 * d2 < -eps) and (d3 * d4 < -eps):
                return True

            clear_touch = (
                on_segment_num(b1, a1, a2) or
                on_segment_num(b2, a1, a2) or
                on_segment_num(a1, b1, b2) or
                on_segment_num(a2, b1, b2)
            )
            if clear_touch and all(Abs(x) > eps for x in (d1, d2, d3, d4)):
                return True

            ambiguous = (
                (Abs(d1) <= eps) or (Abs(d2) <= eps) or
                (Abs(d3) <= eps) or (Abs(d4) <= eps) or
                clear_touch
            )
            if ambiguous:
                from sympy.geometry import Point, Segment
                seg1 = Segment(Point(sympify(a1[0]), sympify(a1[1])),
                               Point(sympify(a2[0]), sympify(a2[1])))
                seg2 = Segment(Point(sympify(b1[0]), sympify(b1[1])),
                               Point(sympify(b2[0]), sympify(b2[1])))
                if seg1.intersection(seg2):
                    return True

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
            # コメント行（例: '# ...'）はスキップ
            if raw.lstrip().startswith('#'):
                continue

            faces = parse_ufd_line_symbolic(raw)
            if faces is None:
                continue

            partial_count += 1

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

            # --- ここから、両端→必要なら内側候補の順に判定 ----------------------

            n = len(polygons)
            result = False  # 行ごとの True/False 最終結果

            if n >= 2:
                # 両端 (0, n-1) が“存在しうる”候補か？
                # 2面間の面をとってきて、すべてに共通する頂点が1以上ならばペア削除
                # （i..j の全ての面の共通頂点が非空なら、元の立体で連鎖的に接触していたとみなし除外）
                endpoint_candidate = (not shares_vertex_chain_all(poly, faces, 0, n - 1))

                if endpoint_candidate:
                    # 両端の重なりをまず判定
                    _, poly_first = polygons[0]
                    _, poly_last  = polygons[-1]
                    end_overlap = polygons_overlap(poly_first, poly_last)

                    if end_overlap:
                        # 他の候補ペア（(0,n-1) 以外で shares_vertex_chain_all == False）に
                        # 重なりが一つも無ければ True
                        ok = True
                        for i in range(n):
                            for j in range(i + 1, n):
                                if i == 0 and j == n - 1:
                                    continue
                                if shares_vertex_chain_all(poly, faces, i, j):
                                    continue
                                _, p1 = polygons[i]
                                _, p2 = polygons[j]
                                if polygons_overlap(p1, p2):
                                    ok = False
                                    break
                            if not ok:
                                break
                        result = ok
                    else:
                        # 両端が重ならないなら False
                        result = False
                else:
                    # 両端自体が候補でないなら False
                    result = False
            else:
                # 面が 0 or 1 の場合は両端が定義できないので False
                result = False

            # 出力：各行につき True/False を1回だけ（標準出力）
            print(f"Partial unfolding: {partial_count} → {result}")

            # --- ここからファイル出力の変更点 -----------------------------------
            # True の行だけ、元の .ufd 行の「中身」を evalf(6) で数値化して1行として出力
            if result:
                # faces: [(gon, edge_id, face_id, x, y, ang), ...]
                out_tokens = [str(len(faces))]
                for (gon, edge_id, face_id, x, y, ang) in faces:
                    out_tokens.append(str(int(gon)))
                    out_tokens.append(str(int(edge_id)))
                    out_tokens.append(str(int(face_id)))
                    # evalf(6) で 6 桁精度（有効桁）に評価
                    out_tokens.append(str(sympify(x).evalf(6)))
                    out_tokens.append(str(sympify(y).evalf(6)))

                    # 角度はラジアン→度へ変換し、[-180, 180] に正規化してから evalf(6)
                    ang_deg = (sympify(ang) * 180 / pi).evalf(12)   # まず度に
                    ang_deg = float(ang_deg)                        # 数値化
                    ang_deg_norm = ((ang_deg + 180.0) % 360.0) - 180.0  # [-180,180]
                    out_tokens.append(str(sympify(ang_deg_norm).evalf(6)))

                fout.write(" ".join(out_tokens) + "\n")
            # False の場合はファイルへは何も書かない

if __name__ == "__main__":
    main()
