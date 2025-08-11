#!/usr/bin/env python3

import sys

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
            int(parts[j + 0]),
            int(parts[j + 1]),
            int(parts[j + 2]),
            float(parts[j + 3]),
            float(parts[j + 4]),
            float(parts[j + 5])
        ))
    return faces

# 各行に対して [n 角形、位置、…、位置、n 角形] の列を取得する関数
# （辺の位置は、時計回りにカウントする）
# Function to obtain a sequence
# [n-gon, position, ..., position, n-gon] for each line
# (Count edge positions in a clockwise direction)
def build_sequence_for_faces(poly, faces):
    seq = []
    adj_edges = poly["adj_edges"]
    k = len(faces)

    for j in range(k):
        gon, edge_id, face_id, *_ = faces[j]
        seq.append(gon)

        if j == 0:
            seq.append(0)
            continue
        if j == k - 1:
            seq.append(-1)
            continue

        pre_edge  = edge_id
        next_edge = faces[j + 1][1]

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

# 多面体の列を反転する関数
# Function to flip the polyhedron sequence
def flip_sequence(seq):
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

# 多面体の列を逆順で見る関数
# Function to view the polyhedron sequence in reverse order
def reverse_sequence(seq):
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

# 4つの対称形（元の形、反転、逆順、反転＋逆順）の中で、辞書順で最も小さいタプルを返す
# Return the lexicographically smallest tuple among
# the 4 symmetry variants (original, flipped, reversed, flip+reversed)
def canonical_key(seq):
    a = seq
    b = flip_sequence(seq)
    c = reverse_sequence(seq)
    d = reverse_sequence(b)
    return min(tuple(a), tuple(b), tuple(c), tuple(d))


def main():
    if len(sys.argv) != 4:
        print("Usage: isomorphic_remover.py <input.adj> <input.ufd> <output.ufd>")
        sys.exit(1)

    adj_path = sys.argv[1]
    poly = read_adj_file(adj_path)

    ufd_path = sys.argv[2]
    out_path = sys.argv[3]

    # 既に出力した unfolding の正規形キー集合（同型性判定用）
    # Set of canonical keys of already output unfoldings
    # (for isomorphism detection)
    seen = set()

    with open(ufd_path, "r", encoding="utf-8") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:
        for raw in fin:
            if not raw.strip():
                continue
            faces = parse_ufd_line(raw)
            if faces is None:
                continue

            seq = build_sequence_for_faces(poly, faces)
            key = canonical_key(seq)

            if key in seen:
                continue
            seen.add(key)

            fout.write(raw.strip() + "\n")


if __name__ == "__main__":
    main()
