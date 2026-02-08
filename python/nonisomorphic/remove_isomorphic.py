"""
Nonisomorphic filtering logic.

Removes isomorphic duplicates from raw.jsonl based on canonical form comparison.
raw.jsonl から正規形比較に基づいて同型な重複を除去します。

Based on scripts/isomorphic_remover.py (legacy implementation).
"""

import json
from pathlib import Path


def load_polyhedron_structure(polyhedron_json_path):
    """
    Loads polyhedron structure from polyhedron.json.
    
    polyhedron.json から多面体構造を読み込みます。
    
    Args:
        polyhedron_json_path (Path): Path to polyhedron.json
    
    Returns:
        dict: Polyhedron structure with:
            - num_faces (int): Number of faces
            - gon_list (list): Number of edges for each face
            - adj_edges (list): Adjacency edges for each face
            - adj_faces (list): Adjacency faces for each face
    """
    with open(polyhedron_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    faces = data["faces"]
    num_faces = len(faces)
    
    # Build gon_list
    # gon_list を構築
    gon_list = [face["gon"] for face in faces]
    
    # Build adj_edges and adj_faces
    # adj_edges と adj_faces を構築
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
    
    return {
        "num_faces": num_faces,
        "gon_list": gon_list,
        "adj_edges": adj_edges,
        "adj_faces": adj_faces
    }


def build_sequence_for_faces(poly, faces):
    """
    Builds a sequence representation for isomorphism comparison.
    
    同型性比較のためのシーケンス表現を構築します。
    
    Args:
        poly (dict): Polyhedron structure
        faces (list): List of face records from JSONL
    
    Returns:
        list: Sequence [gon, position, gon, position, ..., gon, position]
    
    Based on legacy implementation in scripts/isomorphic_remover.py.
    """
    seq = []
    adj_edges = poly["adj_edges"]
    k = len(faces)
    
    for j in range(k):
        face = faces[j]
        gon = face["gon"]
        edge_id = face["edge_id"]
        face_id = face["face_id"]
        
        seq.append(gon)
        
        if j == 0:
            seq.append(0)
            continue
        if j == k - 1:
            seq.append(-1)
            continue
        
        pre_edge = edge_id
        next_edge = faces[j + 1]["edge_id"]
        
        edges = adj_edges[face_id]
        try:
            pos = edges.index(pre_edge)
        except ValueError:
            pos = 0
        
        cnt = 1
        for step in range(1, gon + 1):
            idx = (pos - step) % gon
            if edges[idx] == next_edge:
                break
            cnt += 1
        
        seq.append(cnt)
    
    return seq


def flip_sequence(seq):
    """
    Flips the polyhedron sequence.
    
    多面体シーケンスを反転します。
    
    Args:
        seq (list): Original sequence
    
    Returns:
        list: Flipped sequence
    
    Based on legacy implementation in scripts/isomorphic_remover.py.
    """
    flipped = []
    n = len(seq)
    for i in range(0, n, 2):
        g = seq[i]
        c = seq[i + 1]
        flipped.append(g)
        if i == 0:
            flipped.append(0)
        elif i == n - 2:
            flipped.append(-1)
        else:
            flipped.append(g - c)
    return flipped


def reverse_sequence(seq):
    """
    Reverses the polyhedron sequence.
    
    多面体シーケンスを逆順にします。
    
    Args:
        seq (list): Original sequence
    
    Returns:
        list: Reversed sequence
    
    Based on legacy implementation in scripts/isomorphic_remover.py.
    """
    pairs = [(seq[2*i], seq[2*i + 1]) for i in range(len(seq)//2)]
    k = len(pairs) - 1
    
    rev = []
    for i in range(k, -1, -1):
        g, c = pairs[i]
        if i == k:
            cnt = 0
        elif i == 0:
            cnt = -1
        else:
            cnt = g - c
        rev.append(g)
        rev.append(cnt)
    return rev


def canonical_key(seq):
    """
    Computes the canonical key for isomorphism comparison.
    
    Returns the lexicographically smallest tuple among
    the 4 symmetry variants (original, flipped, reversed, flip+reversed).
    
    同型性比較のための正規キーを計算します。
    
    4つの対称形（元の形、反転、逆順、反転＋逆順）の中で、
    辞書順で最も小さいタプルを返します。
    
    Args:
        seq (list): Sequence representation
    
    Returns:
        tuple: Canonical key (lexicographically smallest)
    
    Based on legacy implementation in scripts/isomorphic_remover.py.
    """
    a = seq
    b = flip_sequence(seq)
    c = reverse_sequence(seq)
    d = reverse_sequence(b)
    return min(tuple(a), tuple(b), tuple(c), tuple(d))


def remove_isomorphic_duplicates(raw_jsonl_path, polyhedron_json_path, output_jsonl_path):
    """
    Removes isomorphic duplicates from raw.jsonl and writes to noniso.jsonl.
    
    raw.jsonl から同型な重複を除去し、noniso.jsonl に書き出します。
    
    Args:
        raw_jsonl_path (Path): Path to raw.jsonl (Phase 1 output)
        polyhedron_json_path (Path): Path to polyhedron.json (polyhedron structure)
        output_jsonl_path (Path): Path to noniso.jsonl (Phase 2 output)
    
    Returns:
        tuple: (num_input_records, num_output_records)
    
    Process:
        1. Load polyhedron structure from polyhedron.json
        2. Read each record from raw.jsonl
        3. Compute canonical key for each record
        4. Skip records with duplicate keys (keep first occurrence)
        5. Write non-duplicate records to noniso.jsonl
    
    処理:
        1. polyhedron.json から多面体構造を読み込む
        2. raw.jsonl から各レコードを読み込む
        3. 各レコードの正規キーを計算
        4. 重複キーのレコードをスキップ（最初の出現を保持）
        5. 非重複レコードを noniso.jsonl に書き出す
    
    Important:
        - Record contents are NOT modified (filtering only)
        - Order is preserved (first occurrence wins)
        - raw.jsonl is read-only (never modified)
    
    重要:
        - レコード内容は変更しない（フィルタリングのみ）
        - 順序は保持される（最初の出現が優先）
        - raw.jsonl は読み取り専用（変更しない）
    """
    # Load polyhedron structure
    # 多面体構造を読み込む
    poly = load_polyhedron_structure(polyhedron_json_path)
    
    # Set of canonical keys of already output unfoldings (for isomorphism detection)
    # 既に出力した unfolding の正規形キー集合（同型性判定用）
    seen = set()
    
    num_input = 0
    num_output = 0
    
    # Read raw.jsonl, filter, and write to noniso.jsonl
    # raw.jsonl を読み込み、フィルタリングして noniso.jsonl に書き出す
    with open(raw_jsonl_path, "r", encoding="utf-8") as fin, \
         open(output_jsonl_path, "w", encoding="utf-8") as fout:
        
        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue
            
            num_input += 1
            
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON parse error at line {line_num}: {e}")
            
            # Extract faces from record
            # レコードから faces を抽出
            faces = record.get("faces", [])
            if not faces:
                continue
            
            # Build sequence representation
            # シーケンス表現を構築
            seq = build_sequence_for_faces(poly, faces)
            
            # Compute canonical key
            # 正規キーを計算
            key = canonical_key(seq)
            
            # Skip if duplicate
            # 重複ならスキップ
            if key in seen:
                continue
            
            seen.add(key)
            
            # Write original record as-is (no modification)
            # 元のレコードをそのまま書き出す（変更しない）
            fout.write(line + "\n")
            num_output += 1
    
    return num_input, num_output
