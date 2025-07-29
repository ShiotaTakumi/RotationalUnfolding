#ifndef POLYHEDRON_HPP
#define POLYHEDRON_HPP

#include <vector>

// 多面体の構造を表す構造体
// A struct representing the structure of a polyhedron.
struct Polyhedron {
    // 多面体の面の数
    // Number of faces in the polyhedron.
    int num_faces;

    // 各面の辺の数（何角形か）
    // Number of edges (gon) for each face.
    std::vector<int> gon_list;

    // 各面を構成する辺 ID のリスト
    // 各面の外向きの法線に対して反時計回りで格納される
    // List of edge IDs that make up each face.
    // Stored in counterclockwise order with respect to the outward normal.
    std::vector<std::vector<int>> adj_edges;

    // 各面に隣接する面 ID のリスト
    // adj_edges と１対１になる順序で格納される
    // List of adjacent face IDs for each face.
    // Stored in a one-to-one order aligned with adj_edges.
    std::vector<std::vector<int>> adj_faces;

    // 指定した面 ID と辺 ID から、
    // その辺が face_id の辺リスト adj_edges 内で何番目に位置するかを返す関数
    // Given a face ID and an edge ID, returns the index of
    // that edge within the edge list adj_edges of the specified face.
    int getEdgeIndex(int face_id, int edge_id) const {
        const auto& edges = adj_edges[face_id];
        for (int i = 0; i < static_cast<int>(edges.size()); ++i) {
            if (edges[i] == edge_id) return i;
        }
        return -1;
    }
};

#endif  // POLYHEDRON_HPP
