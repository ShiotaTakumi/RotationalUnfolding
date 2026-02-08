// ============================================================================
// FaceState.hpp
// ============================================================================
//
// What this file does:
//   Defines the data structure representing the current state of a face
//   during the recursive unfolding search.
//
// このファイルの役割:
//   再帰的な展開探索中の、現在注目している面の状態を表すデータ構造を定義する。
//
// Responsibility in the project:
//   - Stores face placement (x, y, angle, edge_id) for the next recursive step
//   - Stores pruning-related information (remaining_distance, symmetry flags)
//   - Used exclusively during the recursive search process
//
// プロジェクト内での責務:
//   - 次の再帰ステップのための面配置情報 (x, y, angle, edge_id) を保持
//   - 枝刈り関連情報 (remaining_distance, 対称性フラグ) を保持
//   - 再帰探索プロセス中でのみ使用される
//
// Phase 1 における位置づけ:
//   Internal state passed between recursive calls in the search algorithm.
//   Not directly output; only used for search control and pruning.
//   Phase 1では、探索アルゴリズムの再帰呼び出し間で渡される内部状態。
//   直接出力されることはなく、探索制御と枝刈りのみに使用される。
//
// ============================================================================

#ifndef REORG_FACE_STATE_HPP
#define REORG_FACE_STATE_HPP

// ============================================================================
// FaceState
// ============================================================================
//
// Represents the state of a face being considered for addition to the
// current partial unfolding during the recursive search.
//
// 再帰探索中に、現在の部分展開図への追加を検討している面の状態を表す。
//
// Responsibility:
//   - Stores the face to be added (face_id, edge_id)
//   - Stores its geometric placement (x, y, angle)
//   - Stores pruning heuristics (remaining_distance, symmetry flags)
//
// 責務:
//   - 追加対象の面 (face_id, edge_id) を保持
//   - その幾何配置 (x, y, angle) を保持
//   - 枝刈りヒューリスティクス (remaining_distance, 対称性フラグ) を保持
//
// Does NOT handle:
//   - Storage of the entire partial unfolding path
//   - Overlap detection
//   - Output generation
//
// 責務外:
//   - 部分展開図パス全体の保存
//   - 重なり判定
//   - 出力生成
//
// ============================================================================
struct FaceState {
    // ------------------------------------------------------------------------
    // ID of the face being considered for addition.
    // 追加を検討している面の番号。
    // ------------------------------------------------------------------------
    int face_id;

    // ------------------------------------------------------------------------
    // ID of the edge connected to the previously unfolded face.
    // 一つ前に展開された面と接続している辺の番号。
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
    //
    // この面の中心から、一つ前に展開された面の中心への角度（度数法）。
    // ------------------------------------------------------------------------
    double angle;

    // ------------------------------------------------------------------------
    // Sum of diameters of circumscribed circles of all faces not yet used
    // in the partial unfolding, excluding the current face (face_id).
    // Used for distance-based pruning heuristic.
    //
    // 現在の部分展開図で未使用の面（face_idを除く）の外接円の直径の合計。
    // 距離ベースの枝刈りヒューリスティクスに使用される。
    // ------------------------------------------------------------------------
    double remaining_distance;

    // ------------------------------------------------------------------------
    // Flag indicating whether pruning based on y-axis symmetry is enabled.
    //
    // y軸対称性に基づく枝刈りが有効かどうかを示すフラグ。
    // ------------------------------------------------------------------------
    bool symmetry_enabled;

    // ------------------------------------------------------------------------
    // Flag indicating whether the center of any newly unfolded face has
    // deviated from the y-axis (i.e., y != 0).
    // Used only when symmetry_enabled is true.
    // This flag helps prune symmetric branches.
    //
    // 新たに展開した面の中心座標がy軸上以外（y != 0）になったことがあるか
    // を管理するフラグ。
    // symmetry_enabled が true の時にのみ使用される。
    // このフラグは対称な枝の刈り込みに利用される。
    // ------------------------------------------------------------------------
    bool y_moved_off_axis;
};

#endif  // REORG_FACE_STATE_HPP
