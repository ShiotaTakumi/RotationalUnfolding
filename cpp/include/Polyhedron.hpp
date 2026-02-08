// ============================================================================
// Polyhedron.hpp
// ============================================================================
//
// What this file does:
//   Defines the data structure representing a polyhedron's combinatorial
//   structure (faces, edges, adjacency relationships).
//
// このファイルの役割:
//   多面体の組合せ構造（面・辺・隣接関係）を表すデータ構造を定義する。
//
// Responsibility in the project:
//   - Stores polyhedron topology loaded from JSON files
//   - Provides adjacency queries for face-edge relationships
//   - Does NOT handle geometry calculations or unfolding logic
//
// プロジェクト内での責務:
//   - JSON ファイルから読み込まれた多面体のトポロジーを保持
//   - 面と辺の隣接関係のクエリを提供
//   - 幾何計算や展開ロジックは担当しない
//
// Phase 1 における位置づけ:
//   Input data structure for the rotational unfolding algorithm.
//   Phase 1では、回転展開アルゴリズムへの入力データ構造として機能する。
//
// ============================================================================

#ifndef REORG_POLYHEDRON_HPP
#define REORG_POLYHEDRON_HPP

#include <vector>

// ============================================================================
// Polyhedron
// ============================================================================
//
// Represents the combinatorial structure of a polyhedron.
// 多面体の組合せ構造を表す構造体。
//
// Responsibility:
//   - Stores face count, per-face gon (number of edges), edge IDs, and
//     adjacent face IDs
//   - Provides index lookup for edges within a face
//
// 責務:
//   - 面数、各面の辺数（何角形か）、辺ID、隣接面IDを保持
//   - 面内での辺のインデックス検索を提供
//
// Does NOT handle:
//   - Geometric coordinates or 3D positions
//   - Unfolding operations
//
// 責務外:
//   - 幾何座標や3D位置
//   - 展開操作
//
// ============================================================================
struct Polyhedron {
    // ------------------------------------------------------------------------
    // Number of faces in the polyhedron.
    // 多面体の面の数。
    // ------------------------------------------------------------------------
    int num_faces;

    // ------------------------------------------------------------------------
    // Number of edges per face (i.e., what n-gon each face is).
    // 各面の辺の数（何角形か）。
    // ------------------------------------------------------------------------
    std::vector<int> gon_list;

    // ------------------------------------------------------------------------
    // Edge IDs that make up each face.
    // Stored in counterclockwise order with respect to the outward normal.
    //
    // 各面を構成する辺IDのリスト。
    // 外向き法線に対して反時計回りの順で格納される。
    // ------------------------------------------------------------------------
    std::vector<std::vector<int>> adj_edges;

    // ------------------------------------------------------------------------
    // Adjacent face IDs for each face.
    // Stored in one-to-one correspondence with adj_edges.
    //
    // 各面に隣接する面IDのリスト。
    // adj_edges と1対1対応する順序で格納される。
    // ------------------------------------------------------------------------
    std::vector<std::vector<int>> adj_faces;

    // ------------------------------------------------------------------------
    // getEdgeIndex
    // ------------------------------------------------------------------------
    //
    // Input:
    //   face_id  : ID of the face to search within
    //   edge_id  : ID of the edge to find
    //
    // 入力:
    //   face_id  : 検索対象の面ID
    //   edge_id  : 検索する辺ID
    //
    // Output:
    //   Index of the edge within the face's edge list (adj_edges[face_id]).
    //   Returns -1 if the edge is not found.
    //
    // 出力:
    //   面の辺リスト (adj_edges[face_id]) 内での辺のインデックス。
    //   見つからない場合は -1 を返す。
    //
    // Guarantee:
    //   - Returns a valid index [0, gon_list[face_id]) if edge exists
    //   - Returns -1 if edge does not exist in the face
    //   - No side effects
    //
    // 保証:
    //   - 辺が存在する場合、有効なインデックス [0, gon_list[face_id]) を返す
    //   - 辺が面に存在しない場合は -1 を返す
    //   - 副作用なし
    //
    // ------------------------------------------------------------------------
    int getEdgeIndex(int face_id, int edge_id) const {
        const auto& edges = adj_edges[face_id];
        for (int i = 0; i < static_cast<int>(edges.size()); ++i) {
            if (edges[i] == edge_id) return i;
        }
        return -1;
    }
};

#endif  // REORG_POLYHEDRON_HPP
