// ============================================================================
// UnfoldedFace.hpp
// ============================================================================
//
// What this file does:
//   Defines the data structure representing a single face in a partial
//   unfolding, including its geometric placement on the 2D plane.
//
// このファイルの役割:
//   部分展開図における1つの面を表すデータ構造を定義する。
//   2D平面上への幾何配置情報を含む。
//
// Responsibility in the project:
//   - Stores face ID, gon, edge ID, and 2D coordinates (x, y, angle)
//   - Used as an element in the partial unfolding path during search
//   - Does NOT handle unfolding logic or output formatting
//
// プロジェクト内での責務:
//   - 面ID、辺数、辺ID、2D座標 (x, y, angle) を保持
//   - 探索中の部分展開図パスの要素として使用される
//   - 展開ロジックや出力フォーマットは担当しない
//
// Phase 1 における位置づけ:
//   Core data structure for the search algorithm.
//   Instances of this struct are collected and output as JSONL records.
//   Phase 1では、探索アルゴリズムの中核データ構造として機能する。
//   この構造体のインスタンスが収集され、JSONLレコードとして出力される。
//
// ============================================================================

#ifndef REORG_UNFOLDED_FACE_HPP
#define REORG_UNFOLDED_FACE_HPP

// ============================================================================
// UnfoldedFace
// ============================================================================
//
// Represents a single face placed on the 2D plane during unfolding.
// 展開中に2D平面上に配置された1つの面を表す。
//
// Responsibility:
//   - Stores face identification (face_id, gon)
//   - Stores connectivity (edge_id: edge shared with the previous face)
//   - Stores geometric placement (x, y: center coordinates; angle: orientation)
//
// 責務:
//   - 面の識別情報（face_id, gon）を保持
//   - 接続情報（edge_id: 一つ前の面と共有する辺）を保持
//   - 幾何配置（x, y: 中心座標; angle: 向き）を保持
//
// Does NOT handle:
//   - Coordinate transformations
//   - Overlap detection
//   - Output serialization
//
// 責務外:
//   - 座標変換
//   - 重なり判定
//   - 出力のシリアライズ
//
// ============================================================================
struct UnfoldedFace {
    // ------------------------------------------------------------------------
    // ID of the face in the polyhedron.
    // 多面体における面の番号。
    // ------------------------------------------------------------------------
    int face_id;

    // ------------------------------------------------------------------------
    // Number of edges of the face (i.e., what n-gon this face is).
    // 面の辺の数（何角形か）。
    // ------------------------------------------------------------------------
    int gon;

    // ------------------------------------------------------------------------
    // ID of the edge connected to the previously unfolded face.
    // For the first (base) face, this is the base edge used for initialization.
    //
    // 一つ前に展開された面と接続している辺の番号。
    // 最初の（基準）面については、初期化に使用される基準辺。
    // ------------------------------------------------------------------------
    int edge_id;

    // ------------------------------------------------------------------------
    // X-coordinate of the face center on the 2D plane.
    // 2D平面上での面の中心のx座標。
    // ------------------------------------------------------------------------
    double x;

    // ------------------------------------------------------------------------
    // Y-coordinate of the face center on the 2D plane.
    // 2D平面上での面の中心のy座標。
    // ------------------------------------------------------------------------
    double y;

    // ------------------------------------------------------------------------
    // Orientation angle (in degrees) from the center of this face to the
    // center of the previously unfolded face.
    // Represents the direction of the shared edge.
    //
    // この面の中心から、一つ前に展開された面の中心への角度（度数法）。
    // 共有辺の方向を表す。
    // ------------------------------------------------------------------------
    double angle;
};

#endif  // REORG_UNFOLDED_FACE_HPP
