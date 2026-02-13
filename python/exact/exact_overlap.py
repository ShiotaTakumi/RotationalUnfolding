"""
Exact overlap detection logic for rotational unfolding.

Detects overlapping unfoldings using exact arithmetic (SymPy).
SymPy による厳密演算で重なりのある展開図を検出します。

Based on:
    - scripts/generate_exact_expressions.py (exact position reconstruction)
    - scripts/exact_overlap_checker.py (overlap detection logic)

Key differences from legacy:
    - No intermediate file: exact SymPy expressions are built in memory
    - Reads from JSONL format instead of .ufd
    - Vertex-face incidence is computed from polyhedron.json edge adjacency
      (legacy reads V lines from .adj files)
"""

import json
from pathlib import Path

from sympy import S, pi, sin, cos, tan, sympify, Abs
from sympy.geometry import Point, Segment


# ---------------------------------------------------------------------------
# Polyhedron structure loading
# 多面体構造の読み込み
# ---------------------------------------------------------------------------

def load_polyhedron_structure(polyhedron_json_path):
    """
    Loads polyhedron structure from polyhedron.json and computes vertex incidence.

    polyhedron.json から多面体構造を読み込み、頂点共有関係を計算します。

    Args:
        polyhedron_json_path (Path): Path to polyhedron.json

    Returns:
        dict: Polyhedron structure with:
            - num_faces (int): Number of faces
            - gon_list (list): Number of edges for each face
            - adj_edges (list): Adjacency edges for each face
            - adj_faces (list): Adjacency faces for each face
            - vertices (list): Vertex IDs for each face (computed from edge adjacency)
    """
    with open(polyhedron_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    faces = data["faces"]
    num_faces = len(faces)

    gon_list = [face["gon"] for face in faces]

    adj_edges = []
    adj_faces = []
    for face in faces:
        face_adj_edges = []
        face_adj_faces = []
        for neighbor in face["neighbors"]:
            face_adj_edges.append(neighbor["edge_id"])
            face_adj_faces.append(neighbor["face_id"])
        adj_edges.append(face_adj_edges)
        adj_faces.append(face_adj_faces)

    # Compute vertex-face incidence from edge adjacency
    # 辺隣接関係から頂点-面の帰属関係を計算
    vertices = _compute_vertex_incidence(adj_edges, adj_faces, gon_list, num_faces)

    return {
        "num_faces": num_faces,
        "gon_list": gon_list,
        "adj_edges": adj_edges,
        "adj_faces": adj_faces,
        "vertices": vertices,
    }


def _compute_vertex_incidence(adj_edges, adj_faces, gon_list, num_faces):
    """
    Compute vertex-face incidence from edge adjacency using union-find.

    Each face has N corners (one per edge). A "corner" (f, k) is the vertex
    between edge[k] and edge[(k+1) % gon] of face f.

    Two corners from adjacent faces that share an edge endpoint are unioned
    to identify the same polyhedron vertex.

    辺隣接関係から union-find で頂点-面の帰属関係を計算します。

    Returns:
        list of lists: vertices[face_id] = [vertex_id, ...]
    """
    # Union-find data structure
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    # Initialize: each corner is its own root
    for f in range(num_faces):
        for k in range(gon_list[f]):
            parent[(f, k)] = (f, k)

    # Union corners across shared edges
    # Edge e shared between face f (at position i) and face g (at position j):
    #   corner (f, i)           ↔ corner (g, (j-1) % gon_g)
    #   corner (f, (i-1) % gon_f) ↔ corner (g, j)
    processed_edges = set()
    for f in range(num_faces):
        for i in range(len(adj_edges[f])):
            edge_id = adj_edges[f][i]
            if edge_id in processed_edges:
                continue
            processed_edges.add(edge_id)

            g = adj_faces[f][i]
            j = adj_edges[g].index(edge_id)

            gon_f = gon_list[f]
            gon_g = gon_list[g]

            union((f, i), (g, (j - 1) % gon_g))
            union((f, (i - 1) % gon_f), (g, j))

    # Assign vertex IDs from equivalence classes
    vertex_map = {}
    next_vid = 0
    vertices = [[] for _ in range(num_faces)]

    for f in range(num_faces):
        for k in range(gon_list[f]):
            root = find((f, k))
            if root not in vertex_map:
                vertex_map[root] = next_vid
                next_vid += 1
            vertices[f].append(vertex_map[root])

    return vertices


# ---------------------------------------------------------------------------
# Exact position reconstruction (from generate_exact_expressions.py)
# 厳密座標の再構築
# ---------------------------------------------------------------------------

def _inradius(n):
    """
    Inradius of a regular n-gon with edge length 1.
    正 n 角形（辺長 1）の内接円半径。
    """
    return 1 / (2 * tan(pi / n))


def _circumradius(n):
    """
    Circumradius of a regular n-gon with edge length 1.
    正 n 角形（辺長 1）の外接円半径。
    """
    return 1 / (2 * sin(pi / n))


def _step_count_counterclockwise(poly, face_id, pre_edge, next_edge):
    """
    Count counterclockwise steps from pre_edge to next_edge on the given face.

    面 face_id 上で pre_edge から next_edge まで反時計回りにステップ数を数える。

    Args:
        poly: Polyhedron structure
        face_id: Face ID on the original polyhedron
        pre_edge: Edge ID of the entry edge
        next_edge: Edge ID of the exit edge

    Returns:
        int: Number of counterclockwise steps (1-based), or -1 if not found
    """
    edges = poly["adj_edges"][face_id]
    gon = len(edges)

    try:
        pos = edges.index(pre_edge)
    except ValueError:
        pos = -1

    cnt = 1
    for step in range(1, gon + 1):
        idx = (pos + step) % gon
        if edges[idx] == next_edge:
            return cnt
        cnt += 1

    return -1


def build_exact_positions(poly, faces):
    """
    Reconstruct exact SymPy positions from a JSONL face sequence.

    JSONL の面列から厳密な SymPy 座標を再構築します。
    中間ファイルは生成せず、メモリ上で直接計算します。

    This replaces the intermediate file generated by
    scripts/generate_exact_expressions.py.

    Args:
        poly: Polyhedron structure
        faces: List of face dicts from JSONL record
               (each has face_id, gon, edge_id, x, y, angle_deg)

    Returns:
        list of tuples: [(gon, face_id, cx_exact, cy_exact, ang_exact), ...]
                        where cx, cy, ang are exact SymPy expressions
    """
    results = []

    # Base face (first face): origin, angle = 0
    # 基準面（最初の面）: 原点、角度 = 0
    f0 = faces[0]
    cx0, cy0, ang0 = S.Zero, S.Zero, S.Zero
    results.append((f0["gon"], f0["face_id"], cx0, cy0, ang0))

    if len(faces) < 2:
        return results

    # Second face: placed adjacent to base face along x-axis
    # 2番目の面: 基準面の隣に x 軸方向に配置
    f1 = faces[1]
    ir0 = _inradius(f0["gon"])
    ir1 = _inradius(f1["gon"])
    cx1 = ir0 + ir1
    cy1 = S.Zero
    ang1 = -pi
    results.append((f1["gon"], f1["face_id"], cx1, cy1, ang1))

    prev_gon = f1["gon"]
    prev_face_id = f1["face_id"]
    prev_edge_id = f1["edge_id"]
    prev_cx, prev_cy, prev_ang = cx1, cy1, ang1

    # Third and subsequent faces: computed incrementally
    # 3番目以降の面: 逐次的に計算
    for idx in range(2, len(faces)):
        fi = faces[idx]
        gon_i = fi["gon"]
        edge_i = fi["edge_id"]
        face_i = fi["face_id"]

        # Count counterclockwise steps from entry edge to exit edge
        # 入口辺から出口辺までの反時計回りステップ数
        cnt = _step_count_counterclockwise(poly, prev_face_id, prev_edge_id, edge_i)

        # Angle toward the center of the next face
        # 次の面の中心方向への角度
        theta_center = prev_ang - cnt * (2 * pi / prev_gon)

        # Center coordinates of the next face
        # 次の面の中心座標
        ir_prev = _inradius(prev_gon)
        ir_curr = _inradius(gon_i)
        delta = ir_prev + ir_curr
        cx_i = prev_cx + delta * cos(theta_center)
        cy_i = prev_cy + delta * sin(theta_center)

        # Orientation angle of the next face
        # 次の面の向きの角度
        ang_i = theta_center - pi

        results.append((gon_i, face_i, cx_i, cy_i, ang_i))

        prev_gon = gon_i
        prev_face_id = face_i
        prev_edge_id = edge_i
        prev_cx, prev_cy, prev_ang = cx_i, cy_i, ang_i

    return results


def _get_vertices_of_face(gon, cx, cy, ang):
    """
    Compute exact vertices of a regular n-gon given center and orientation angle.

    中心座標と向きの角度から正 n 角形の厳密な頂点座標を計算します。

    Ported from scripts/exact_overlap_checker.py: get_vertices_of_face()

    Args:
        gon: Number of sides
        cx, cy: Center coordinates (exact SymPy expressions)
        ang: Orientation angle in radians (exact SymPy expression)

    Returns:
        list of tuples: [(x0, y0), (x1, y1), ...] with exact SymPy expressions
    """
    r = _circumradius(gon)
    offset = pi / gon
    vertices = []
    for k in range(gon):
        theta = ang + offset + 2 * pi * k / gon
        xk = cx + r * cos(theta)
        yk = cy + r * sin(theta)
        vertices.append((xk, yk))
    return vertices


# ---------------------------------------------------------------------------
# Intersection classification
# 交差種別の分類
# ---------------------------------------------------------------------------

def _classify_intersection(intersection_result, seg1, seg2):
    """
    Classify the type of intersection between two segments.

    SymPy の Segment.intersection() の結果から交差種別を分類します。

    Classification rules:
        - Segment in result with positive length → "edge-edge"
        - Segment in result with zero length (degenerate) → classified as point contact
        - Point in result (or degenerate Segment point):
            - Endpoint of both segments → "vertex-vertex" (vertex contact)
            - Endpoint of one segment only → "edge-vertex" (vertex on edge interior)
            - Interior of both segments → "face-face" (proper crossing)

    分類規則:
        - 結果に Segment（正の長さ）→ "edge-edge"（辺の同一直線上重なり）
        - 結果に Segment（長さ 0、退化）→ 点接触として分類
        - 結果が Point（または退化 Segment の点）:
            - 両セグメントの端点 → "vertex-vertex"（頂点接触）
            - 片方のみの端点 → "edge-vertex"（辺内部への点接触）
            - どちらの端点でもない → "face-face"（辺が内部で交差）

    Args:
        intersection_result: List of SymPy geometric objects from Segment.intersection()
        seg1: First Segment
        seg2: Second Segment

    Returns:
        str: One of "face-face", "edge-edge", "vertex-vertex", "edge-vertex"
    """
    # Helper: classify a single contact point by endpoint membership
    # ヘルパー: 端点帰属で1つの接触点を分類する
    def _classify_point(pt):
        is_ep1 = pt.equals(seg1.p1) or pt.equals(seg1.p2)
        is_ep2 = pt.equals(seg2.p1) or pt.equals(seg2.p2)
        if is_ep1 and is_ep2:
            return "vertex-vertex"
        elif is_ep1 or is_ep2:
            return "edge-vertex"
        else:
            return "face-face"  # interior crossing

    # Check for Segment (collinear overlap) first — highest structural priority
    # まず Segment（同一直線上の重なり）をチェック — 構造的に最優先
    # A degenerate Segment (length 0) is treated as a Point contact instead.
    # 退化 Segment（長さ 0）は Point 接触として分類する。
    for obj in intersection_result:
        if isinstance(obj, Segment):
            dx = obj.p1.x - obj.p2.x
            dy = obj.p1.y - obj.p2.y
            length_sq = sympify(dx**2 + dy**2)
            if length_sq != 0:
                return "edge-edge"
            # Degenerate Segment (length 0) — classify as point contact
            # 退化 Segment（長さ 0）— 点接触として分類
            return _classify_point(obj.p1)

    # All remaining elements should be Points — classify by endpoint membership
    # 残りはすべて Point のはず — 端点帰属で分類
    for obj in intersection_result:
        if isinstance(obj, Point):
            return _classify_point(obj)

    # Conservative fallback (should not normally be reached)
    # 保守的なフォールバック（通常到達しない）
    return "face-face"


# ---------------------------------------------------------------------------
# Vertex chain checking
# 頂点連鎖チェック
# ---------------------------------------------------------------------------

def _shares_vertex_chain_all(poly, face_ids, i, j):
    """
    Check if ALL faces from index i to j (in the unfolding sequence)
    share at least one common vertex on the original polyhedron.

    展開列のインデックス i から j までの全ての面が、
    元の多面体上で少なくとも1つの共通頂点を持つかを判定します。

    If True, these faces are topologically adjacent and overlap between
    them is expected (should be skipped during overlap checking).

    Ported from scripts/exact_overlap_checker.py: shares_vertex_chain_all()

    Args:
        poly: Polyhedron structure (must include "vertices")
        face_ids: List of face IDs in unfolding order
        i, j: Start and end indices (inclusive)

    Returns:
        bool: True if all faces from i to j share a common vertex
    """
    V = poly["vertices"]
    common = set(V[face_ids[i]])
    for t in range(i + 1, j + 1):
        common &= set(V[face_ids[t]])
        if not common:
            return False
    return len(common) > 0


# ---------------------------------------------------------------------------
# Polygon overlap detection (hybrid numeric + exact)
# 多角形の重なり検出（ハイブリッド数値＋厳密）
# ---------------------------------------------------------------------------

def _polygons_overlap(poly1_verts, poly2_verts):
    """
    Check if two polygons overlap using hybrid numeric + exact approach.

    ハイブリッド（高精度数値 + SymPy 厳密）アプローチで
    2つの多角形の重なりを判定します。

    Ported faithfully from scripts/exact_overlap_checker.py: polygons_overlap()

    Detection criteria (strict):
        1. Edge-edge crossing (positive area intersection) → "face-face"
        2. Edge collinear overlap (positive length) → "edge-edge"
        3. Vertex-vertex contact → "vertex-vertex"
        4. Vertex on edge interior → "edge-vertex"
        → Any non-empty intersection is detected and classified

    判定基準（strict）：
        1. 辺-辺の交差（正面積の交差）→ "face-face"
        2. 辺の同一直線上の重なり（正の長さ）→ "edge-edge"
        3. 頂点-頂点の接触 → "vertex-vertex"
        4. 辺内部への頂点接触 → "edge-vertex"
        → 交差が空でなければ検出し、種別を分類する

    Classification priority (strongest wins):
        face-face (3) > edge-edge (2) > edge-vertex / vertex-vertex (1)
    All edge pairs are scanned; the strongest kind found is returned.
    Only face-face may short-circuit (it is the maximum priority).

    分類優先度（最も強いものが返される）：
        face-face (3) > edge-edge (2) > edge-vertex / vertex-vertex (1)
    全辺ペアを走査し、最も強い種別を返す。
    face-face のみ即座に return してよい（最大優先度のため）。

    TODO: Future extension — option to exclude touch (vertex-vertex / edge-vertex)
          from overlap definition. Currently all contact types are treated as overlap.
    TODO: Future extension — write classification results to exact.jsonl records.

    Args:
        poly1_verts: List of (x, y) tuples for polygon 1 (exact SymPy)
        poly2_verts: List of (x, y) tuples for polygon 2 (exact SymPy)

    Returns:
        tuple: (overlap: bool, kind: str or None)
            overlap: True if any non-empty intersection exists
            kind: One of "face-face", "edge-edge", "vertex-vertex", "edge-vertex",
                  or None if no overlap
    """
    # --- Overlap kind priority (higher = stronger) ---
    # 重なり種別の優先度（大きいほど強い）
    _KIND_PRIORITY = {
        "vertex-vertex": 1,
        "edge-vertex": 1,
        "edge-edge": 2,
        "face-face": 3,
    }

    # --- Numeric phase settings ---
    prec_fast = 80
    eps = sympify('1e-30')

    def _num(x):
        return sympify(x).evalf(prec_fast)

    def edges_of(poly):
        m = len(poly)
        return [(poly[i], poly[(i + 1) % m]) for i in range(m)]

    # AABB fast rejection (numeric)
    def aabb_overlap(a1, a2, b1, b2):
        ax1, ay1 = _num(a1[0]), _num(a1[1])
        ax2, ay2 = _num(a2[0]), _num(a2[1])
        bx1, by1 = _num(b1[0]), _num(b1[1])
        bx2, by2 = _num(b2[0]), _num(b2[1])
        minAx, maxAx = min(ax1, ax2), max(ax1, ax2)
        minAy, maxAy = min(ay1, ay2), max(ay1, ay2)
        minBx, maxBx = min(bx1, bx2), max(bx1, bx2)
        minBy, maxBy = min(by1, by2), max(by1, by2)
        return not (
            (maxAx < minBx - eps) or
            (maxBx < minAx - eps) or
            (maxAy < minBy - eps) or
            (maxBy < minAy - eps)
        )

    # Cross product (signed area * 2)
    def orient(a, b, c):
        ax, ay = _num(a[0]), _num(a[1])
        bx, by = _num(b[0]), _num(b[1])
        cx, cy = _num(c[0]), _num(c[1])
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    # Point-on-segment test (numeric): collinear & projection within range
    def on_segment_num(p, a, b):
        ax, ay = _num(a[0]), _num(a[1])
        bx, by = _num(b[0]), _num(b[1])
        px, py = _num(p[0]), _num(p[1])

        cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
        if Abs(cross) > eps:
            return False

        dot = (px - ax) * (bx - ax) + (py - ay) * (by - ay)
        seg2 = (bx - ax) * (bx - ax) + (by - ay) * (by - ay)
        if dot < -eps or dot > seg2 + eps:
            return False
        return True

    # --- Edge pair scan: collect strongest overlap kind ---
    # 全辺ペアを走査し、最も強い種別を収集する
    edges1 = edges_of(poly1_verts)
    edges2 = edges_of(poly2_verts)

    best_kind = None       # strongest kind found so far
    best_priority = 0      # priority of best_kind

    for (a1, a2) in edges1:
        for (b1, b2) in edges2:
            if not aabb_overlap(a1, a2, b1, b2):
                continue

            d1 = orient(a1, a2, b1)
            d2 = orient(a1, a2, b2)
            d3 = orient(b1, b2, a1)
            d4 = orient(b1, b2, a2)

            # Clear crossing: both endpoints of each segment are on opposite sides
            # → polygon interiors overlap (face-face) — maximum priority, return immediately
            if (d1 * d2 < -eps) and (d3 * d4 < -eps):
                return (True, "face-face")

            # Determine if this edge pair needs exact classification
            clear_touch = (
                on_segment_num(b1, a1, a2) or
                on_segment_num(b2, a1, a2) or
                on_segment_num(a1, b1, b2) or
                on_segment_num(a2, b1, b2)
            )

            # Ambiguous case: fall back to exact SymPy geometry for classification
            ambiguous = (
                (Abs(d1) <= eps) or (Abs(d2) <= eps) or
                (Abs(d3) <= eps) or (Abs(d4) <= eps) or
                clear_touch
            )
            if ambiguous:
                # Use direct parametric intersection instead of Segment.intersection()
                # to avoid slow/error-prone SymPy geometry operations
                # 遅い/エラーが出やすい SymPy geometry 演算を回避するため、
                # 直接パラメトリック表現で交差判定

                # Convert to exact SymPy expressions
                # 厳密な SymPy 式に変換
                p1x, p1y = sympify(a1[0]), sympify(a1[1])
                p2x, p2y = sympify(a2[0]), sympify(a2[1])
                q1x, q1y = sympify(b1[0]), sympify(b1[1])
                q2x, q2y = sympify(b2[0]), sympify(b2[1])

                # Direction vectors
                # 方向ベクトル
                dx1 = p2x - p1x
                dy1 = p2y - p1y
                dx2 = q2x - q1x
                dy2 = q2y - q1y

                # Check for intersection using parametric form
                # パラメトリック形式で交差判定
                # Segment 1: P1 + t*(P2-P1), t ∈ [0,1]
                # Segment 2: Q1 + s*(Q2-Q1), s ∈ [0,1]
                # Solve: P1 + t*d1 = Q1 + s*d2

                # Cross product for determinant: d1 × d2
                # 行列式のための外積: d1 × d2
                det = dx1 * dy2 - dy1 * dx2

                # Check if segments are parallel (det ≈ 0)
                # 平行かチェック (det ≈ 0)
                if Abs(det) < sympify('1e-50'):
                    # Parallel or collinear - check for overlap
                    # 平行または同一直線上 - 重なりをチェック
                    # Use simpler collinear overlap detection
                    # より単純な同一直線重なり検出を使用

                    # Check if endpoints are on the other segment
                    # 端点が他のセグメント上にあるかチェック
                    endpoints = [
                        (p1x, p1y, "v1"), (p2x, p2y, "v2"),
                        (q1x, q1y, "v3"), (q2x, q2y, "v4")
                    ]

                    # Count how many endpoints coincide or lie on the other segment
                    # 一致または他のセグメント上にある端点の数をカウント
                    touch_count = 0
                    eps_val = sympify('1e-50')
                    one = sympify(1)

                    for px, py, label in endpoints[:2]:
                        # Check if (px, py) is on segment 2
                        # (px, py) がセグメント2上にあるかチェック
                        try:
                            if Abs(dx2) > Abs(dy2):
                                if Abs(dx2) > eps_val:
                                    s_val = (px - q1x) / dx2
                                    # Use is_nonnegative to check range
                                    # is_nonnegative で範囲チェック
                                    s_min = (s_val + eps_val).simplify()
                                    s_max = (one + eps_val - s_val).simplify()
                                    if (s_min.is_nonnegative is not False) and (s_max.is_nonnegative is not False):
                                        if Abs(py - (q1y + s_val * dy2)) < eps_val:
                                            touch_count += 1
                            else:
                                if Abs(dy2) > eps_val:
                                    s_val = (py - q1y) / dy2
                                    s_min = (s_val + eps_val).simplify()
                                    s_max = (one + eps_val - s_val).simplify()
                                    if (s_min.is_nonnegative is not False) and (s_max.is_nonnegative is not False):
                                        if Abs(px - (q1x + s_val * dx2)) < eps_val:
                                            touch_count += 1
                        except:
                            # If checking fails, conservatively assume touch
                            # チェックが失敗した場合、保守的に接触と仮定
                            touch_count += 1

                    if touch_count >= 2:
                        # Edge-edge overlap (collinear)
                        # 辺-辺の重なり（同一直線上）
                        kind = "edge-edge"
                        p = _KIND_PRIORITY.get(kind, 0)
                        if p > best_priority:
                            best_kind = kind
                            best_priority = p
                    elif touch_count == 1:
                        # Single point contact
                        # 1点接触
                        kind = "edge-vertex"
                        p = _KIND_PRIORITY.get(kind, 0)
                        if p > best_priority:
                            best_kind = kind
                            best_priority = p
                else:
                    # Non-parallel: solve for intersection point
                    # 非平行: 交点を解く
                    # t = ((Q1-P1) × d2) / (d1 × d2)
                    # s = ((Q1-P1) × d1) / (d1 × d2)

                    cross1 = (q1x - p1x) * dy2 - (q1y - p1y) * dx2
                    cross2 = (q1x - p1x) * dy1 - (q1y - p1y) * dx1

                    t = cross1 / det
                    s = cross2 / det

                    # Check if intersection is within both segments
                    # 交点が両セグメント内にあるかチェック
                    eps_val = sympify('1e-50')
                    one = sympify(1)

                    # Use simplify to resolve the boolean
                    # simplify で真偽値を確定
                    try:
                        t_min = (t + eps_val).simplify()
                        t_max = (one + eps_val - t).simplify()
                        s_min = (s + eps_val).simplify()
                        s_max = (one + eps_val - s).simplify()

                        # Check if all are non-negative
                        # すべてが非負かチェック
                        t_in_range = (t_min.is_nonnegative is not False) and (t_max.is_nonnegative is not False)
                        s_in_range = (s_min.is_nonnegative is not False) and (s_max.is_nonnegative is not False)
                    except:
                        # If simplify fails, conservatively assume in range
                        # simplify が失敗した場合、保守的に範囲内と仮定
                        t_in_range = True
                        s_in_range = True

                    if t_in_range and s_in_range:
                        # Classify intersection type
                        # 交差種別を分類

                        # Check if intersection is at endpoints
                        # 交点が端点にあるかチェック
                        t_is_endpoint = (Abs(t) < eps_val) or (Abs(t - one) < eps_val)
                        s_is_endpoint = (Abs(s) < eps_val) or (Abs(s - one) < eps_val)

                        if t_is_endpoint and s_is_endpoint:
                            kind = "vertex-vertex"
                        elif t_is_endpoint or s_is_endpoint:
                            kind = "edge-vertex"
                        else:
                            kind = "face-face"  # Interior crossing

                        p = _KIND_PRIORITY.get(kind, 0)
                        if p >= 3:
                            # face-face — maximum priority, return immediately
                            return (True, kind)
                        if p > best_priority:
                            best_kind = kind
                            best_priority = p

    if best_kind is not None:
        return (True, best_kind)

    return (False, None)


# ---------------------------------------------------------------------------
# Record-level overlap check
# レコード単位の重なり判定
# ---------------------------------------------------------------------------

def check_record_overlap(poly, faces):
    """
    Check a single JSONL record for exact overlap.

    1つの JSONL レコードの厳密重なりを判定します。

    A record is KEPT (returns True) if:
        1. The first and last faces overlap (expected endpoint overlap)
        2. No other non-adjacent face pair has any overlap

    A record is REMOVED (returns False) if:
        1. The first and last faces do NOT overlap (false positive from
           approximate detection)
        2. OR some non-adjacent pair (other than the endpoints) overlaps
           (spurious overlap that invalidates the unfolding)

    Ported from scripts/exact_overlap_checker.py main loop.

    Args:
        poly: Polyhedron structure (with vertices)
        faces: List of face dicts from JSONL record

    Returns:
        bool: True if the record should be kept in exact.jsonl
    """
    # Reconstruct exact positions
    exact_positions = build_exact_positions(poly, faces)
    n = len(exact_positions)

    if n < 2:
        return False

    # Build polygon vertices and face ID list
    polygons = []
    face_ids = []
    for (gon, face_id, cx, cy, ang) in exact_positions:
        verts = _get_vertices_of_face(gon, cx, cy, ang)
        polygons.append(verts)
        face_ids.append(face_id)

    # Check if endpoint pair (first and last) is a valid candidate
    # (they must NOT all share a common vertex through the chain)
    endpoint_candidate = not _shares_vertex_chain_all(poly, face_ids, 0, n - 1)

    if not endpoint_candidate:
        return False

    # Check endpoint overlap (first and last faces must overlap)
    end_overlap, _end_kind = _polygons_overlap(polygons[0], polygons[-1])

    if not end_overlap:
        return False

    # Check that no other non-adjacent pair overlaps
    for i in range(n):
        for j in range(i + 1, n):
            if i == 0 and j == n - 1:
                continue  # skip endpoint pair (already verified)
            if _shares_vertex_chain_all(poly, face_ids, i, j):
                continue  # skip topologically adjacent pairs
            spurious, _sp_kind = _polygons_overlap(polygons[i], polygons[j])
            if spurious:
                return False  # spurious overlap found → remove record
        # Early exit if spurious overlap was found in inner loop
        # (Python doesn't have labeled break, so we check after inner loop)
        # Actually, the inner break only exits the inner loop.
        # We need a flag to break the outer loop too.

    # If we get here, the record is valid: endpoint overlap with no spurious overlaps
    return True


def check_record_overlap_safe(poly, faces):
    """
    Check a single JSONL record for exact overlap with classification info.

    1つの JSONL レコードの厳密重なり判定を行い、分類情報を返します。
    二重ループの break を正しく処理するバージョン。

    Args:
        poly: Polyhedron structure (with vertices)
        faces: List of face dicts from JSONL record

    Returns:
        tuple: (keep: bool, info: dict)
            keep: True if the record should be kept in exact.jsonl
            info: Classification details with keys:
                - "reason" (str): Why the record was kept or removed
                - "endpoint_kind" (str or None): Overlap kind of endpoint pair
                - "spurious" (tuple or None): (i, j, kind) of first spurious overlap
    """
    # Reconstruct exact positions
    exact_positions = build_exact_positions(poly, faces)
    n = len(exact_positions)

    if n < 2:
        return (False, {
            "reason": "too few faces",
            "endpoint_kind": None,
            "spurious": None,
        })

    # Build polygon vertices and face ID list
    polygons = []
    face_ids = []
    for (gon, face_id, cx, cy, ang) in exact_positions:
        verts = _get_vertices_of_face(gon, cx, cy, ang)
        polygons.append(verts)
        face_ids.append(face_id)

    # Check if endpoint pair is a valid candidate
    endpoint_candidate = not _shares_vertex_chain_all(poly, face_ids, 0, n - 1)

    if not endpoint_candidate:
        return (False, {
            "reason": "endpoint vertex chain",
            "endpoint_kind": None,
            "spurious": None,
        })

    # Check endpoint overlap with classification
    end_overlap, end_kind = _polygons_overlap(polygons[0], polygons[-1])

    if not end_overlap:
        return (False, {
            "reason": "no endpoint overlap",
            "endpoint_kind": None,
            "spurious": None,
        })

    # Check no other non-adjacent pair overlaps
    ok = True
    spurious_info = None
    for i in range(n):
        for j in range(i + 1, n):
            if i == 0 and j == n - 1:
                continue
            if _shares_vertex_chain_all(poly, face_ids, i, j):
                continue
            overlap, kind = _polygons_overlap(polygons[i], polygons[j])
            if overlap:
                ok = False
                spurious_info = (i, j, kind)
                break
        if not ok:
            break

    if ok:
        return (True, {
            "reason": "valid",
            "endpoint_kind": end_kind,
            "spurious": None,
        })
    else:
        return (False, {
            "reason": "spurious overlap",
            "endpoint_kind": end_kind,
            "spurious": spurious_info,
        })


# ---------------------------------------------------------------------------
# Main filter function
# メインフィルター関数
# ---------------------------------------------------------------------------

def filter_exact_overlaps(noniso_jsonl_path, polyhedron_json_path, exact_jsonl_path):
    """
    Filter noniso.jsonl to exact.jsonl by checking for exact overlaps.

    noniso.jsonl を読み込み、厳密重なり判定を行い、exact.jsonl を生成します。

    Keeps only records where:
        1. The first and last faces overlap (expected endpoint overlap)
        2. No other non-adjacent face pair overlaps

    保持するレコード:
        1. 最初と最後の面が重なる（期待される端点重なり）
        2. 他の非隣接面ペアに重なりがない

    Args:
        noniso_jsonl_path (Path): Path to noniso.jsonl (Phase 2 output, read-only)
        polyhedron_json_path (Path): Path to polyhedron.json
        exact_jsonl_path (Path): Path to exact.jsonl (Phase 3 output)

    Returns:
        tuple: (num_input_records, num_output_records)

    Output record format:
        Each surviving record is augmented with an "exact_overlap" field:
            {"exact_overlap": {"kind": "face-face"}}
        The kind is one of: "face-face", "edge-edge", "vertex-vertex", "edge-vertex".
        This field represents the overlap type of the endpoint pair (first and last faces).
        All other fields from noniso.jsonl are preserved as-is.

    出力レコード形式:
        保持されるレコードには "exact_overlap" フィールドが付与される：
            {"exact_overlap": {"kind": "face-face"}}
        kind は "face-face" / "edge-edge" / "vertex-vertex" / "edge-vertex" のいずれか。
        このフィールドは端点ペア（最初と最後の面）の重なり種別を表す。
        noniso.jsonl のその他のフィールドはそのまま保持される。

    Important:
        - Order is preserved
        - noniso.jsonl is read-only (never modified)
        - Output record count is determined solely by overlap detection (unchanged)

    重要:
        - 順序は保持される
        - noniso.jsonl は読み取り専用（変更しない）
        - 出力レコード件数は重なり判定のみで決定される（変更なし）

    TODO: Future extension — option to exclude touch (vertex-vertex / edge-vertex)
          from overlap definition, controlled by a CLI flag or config parameter.
    """
    # Load polyhedron structure (including vertex incidence)
    # 多面体構造を読み込む（頂点共有関係を含む）
    poly = load_polyhedron_structure(polyhedron_json_path)

    # Count total records for progress reporting
    # 進捗表示のための総レコード数のカウント
    with open(noniso_jsonl_path, "r", encoding="utf-8") as f:
        total = sum(1 for line in f if line.strip())

    num_input = 0
    num_output = 0

    with open(noniso_jsonl_path, "r", encoding="utf-8") as fin, \
         open(exact_jsonl_path, "w", encoding="utf-8") as fout:

        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            num_input += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON parse error at line {line_num}: {e}")

            faces = record.get("faces", [])
            if not faces:
                continue

            print(f"  Record {num_input}/{total}...", end="", flush=True)

            # Check exact overlap using the safe double-loop version
            # (returns classification info for logging)
            keep, info = check_record_overlap_safe(poly, faces)

            if keep:
                # Augment record with overlap classification
                # レコードに重なり種別を付与して書き出す
                endpoint_kind = info.get("endpoint_kind", "unknown")
                record["exact_overlap"] = {"kind": endpoint_kind}
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                num_output += 1
                # Log with endpoint overlap classification
                # 端点重なりの分類情報付きでログ出力
                print(f" KEEP (endpoint: {endpoint_kind})")
            else:
                # Log with removal reason and classification
                # 除去理由と分類情報付きでログ出力
                reason = info.get("reason", "unknown")
                if reason == "spurious overlap":
                    sp = info.get("spurious")
                    if sp:
                        sp_i, sp_j, sp_kind = sp
                        print(f" REMOVE (spurious {sp_kind} at [{sp_i}, {sp_j}])")
                    else:
                        print(f" REMOVE ({reason})")
                else:
                    print(f" REMOVE ({reason})")

    return num_input, num_output
