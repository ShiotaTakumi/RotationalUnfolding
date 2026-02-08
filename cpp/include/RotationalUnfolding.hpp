// ============================================================================
// RotationalUnfolding.hpp
// ============================================================================
//
// What this file does:
//   Implements the core algorithm for exploring path-shaped partial unfoldings
//   of a given polyhedron using rotational unfolding with pruning heuristics.
//
// このファイルの役割:
//   枝刈りヒューリスティクスを用いた回転展開により、与えられた多面体の
//   パス状の部分展開図を探索する中核アルゴリズムを実装する。
//
// Responsibility in the project:
//   - Executes the recursive search for partial unfoldings
//   - Checks for overlaps between the base face and the last face
//   - Applies distance-based and symmetry-based pruning
//   - Outputs JSONL records for candidate unfoldings
//   - Does NOT handle file I/O or CLI argument parsing
//
// プロジェクト内での責務:
//   - 部分展開図の再帰的探索を実行
//   - 基準面と最後の面の重なりをチェック
//   - 距離ベースおよび対称性ベースの枝刈りを適用
//   - 候補展開図をJSONLレコードとして出力
//   - ファイルI/OやCLI引数の解析は担当しない
//
// Phase 1 における位置づけ:
//   Core algorithm for Phase 1. This class is the heart of the search process.
//   It produces raw partial unfoldings that will be post-processed in Phase 2+.
//   Phase 1の中核アルゴリズム。この検索プロセスの心臓部である。
//   Phase 2以降で後処理される生の部分展開図を生成する。
//
// ============================================================================

#ifndef REORG_ROTATIONAL_UNFOLDING_HPP
#define REORG_ROTATIONAL_UNFOLDING_HPP

#include "FaceState.hpp"
#include "UnfoldedFace.hpp"
#include "Polyhedron.hpp"
#include "GeometryUtil.hpp"
#include "JsonUtil.hpp"
#include <vector>
#include <iostream>
#include <cmath>
#include <sstream>

// ============================================================================
// RotationalUnfolding
// ============================================================================
//
// Explores path-shaped partial edge unfoldings of a polyhedron.
// This class performs a depth-first search starting from a specified
// base face and base edge, checking for overlaps at both endpoints.
//
// 多面体のパス状の部分辺展開図を探索する。
// このクラスは、指定された基準面と基準辺から開始する深さ優先探索を実行し、
// 両端点での重なりをチェックする。
//
// Responsibility:
//   - Manages the recursive search state
//   - Applies pruning heuristics (distance, symmetry)
//   - Detects potential overlaps based on circumradius proximity
//   - Outputs candidate unfoldings in JSONL format
//
// 責務:
//   - 再帰探索の状態を管理
//   - 枝刈りヒューリスティクス（距離、対称性）を適用
//   - 外接円半径の近接性に基づいて潜在的な重なりを検出
//   - 候補展開図をJSONL形式で出力
//
// Does NOT handle:
//   - Exact overlap verification (deferred to Phase 3)
//   - Isomorphism detection (deferred to Phase 2)
//   - File I/O management
//
// 責務外:
//   - 厳密な重なり検証（Phase 3に委譲）
//   - 同型性判定（Phase 2に委譲）
//   - ファイルI/O管理
//
// Algorithm overview:
//   1. Start with the base face placed at the origin
//   2. Recursively add adjacent faces, rotating around shared edges
//   3. Check if the last face's circumradius overlaps with the base face
//   4. If overlap is detected, output the partial unfolding
//   5. Apply pruning to avoid redundant or impossible branches
//
// アルゴリズムの概要:
//   1. 原点に配置された基準面から開始
//   2. 共有辺の周りを回転しながら、隣接面を再帰的に追加
//   3. 最後の面の外接円が基準面と重なるかをチェック
//   4. 重なりが検出された場合、部分展開図を出力
//   5. 冗長または不可能な枝を避けるために枝刈りを適用
//
// ============================================================================
class RotationalUnfolding {
public:
    // ------------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------------
    //
    // Input:
    //   poly              : Reference to the polyhedron structure (immutable)
    //   base_face         : ID of the base face (placed at origin)
    //   base_edge         : ID of the base edge (used for the first rotation)
    //   enable_symmetry   : Whether to enable y-axis symmetry pruning
    //   y_moved_off_axis  : Initial state of y-movement tracking (usually same as enable_symmetry)
    //
    // 入力:
    //   poly              : 多面体構造への参照（不変）
    //   base_face         : 基準面のID（原点に配置）
    //   base_edge         : 基準辺のID（最初の回転に使用）
    //   enable_symmetry   : y軸対称性枝刈りを有効にするか
    //   y_moved_off_axis  : y移動追跡の初期状態（通常は enable_symmetry と同じ）
    //
    // Guarantee:
    //   - Initializes the search state
    //   - Does not modify the polyhedron structure
    //   - No immediate computation; call runRotationalUnfolding to start search
    //
    // 保証:
    //   - 探索状態を初期化
    //   - 多面体構造を変更しない
    //   - 即座の計算は行わない。探索を開始するには runRotationalUnfolding を呼ぶ
    //
    // ------------------------------------------------------------------------
    RotationalUnfolding(
        const Polyhedron& poly,
        int base_face,
        int base_edge,
        bool enable_symmetry,
        bool y_moved_off_axis
    )
        : polyhedron(poly),
        base_face_id(base_face),
        base_edge_id(base_edge),
        symmetry_enabled(enable_symmetry),
        y_moved_off_axis(y_moved_off_axis) {}

    // ------------------------------------------------------------------------
    // runRotationalUnfolding
    // ------------------------------------------------------------------------
    //
    // Input:
    //   jsonl_output : Output stream for JSONL records (one line per candidate unfolding)
    //
    // 入力:
    //   jsonl_output : JSONLレコード用の出力ストリーム（候補展開図ごとに1行）
    //
    // Output:
    //   Writes JSONL records to jsonl_output for all candidate partial unfoldings
    //   found during the search.
    //
    // 出力:
    //   探索中に見つかったすべての候補部分展開図についてJSONLレコードを
    //   jsonl_output に書き込む。
    //
    // Guarantee:
    //   - Explores all valid unfolding paths starting from the base face/edge
    //   - Each output record represents a candidate where the base face and
    //     the last face's circumradii are close enough to potentially overlap
    //   - Applies pruning heuristics to reduce search space
    //   - Does not modify the polyhedron structure
    //   - May write zero or more JSONL records depending on the polyhedron
    //
    // 保証:
    //   - 基準面・辺から始まるすべての有効な展開パスを探索
    //   - 各出力レコードは、基準面と最後の面の外接円が潜在的に重なるほど
    //     近い候補を表す
    //   - 探索空間を削減するために枝刈りヒューリスティクスを適用
    //   - 多面体構造を変更しない
    //   - 多面体に応じて0個以上のJSONLレコードを書き込む可能性がある
    //
    // ------------------------------------------------------------------------
    void runRotationalUnfolding(std::ostream& jsonl_output) {

        // Initialize face usage tracking (true = unused, false = used)
        // 面の使用状況追跡を初期化（true = 未使用、false = 使用済み）
        std::vector<bool> face_usage(polyhedron.num_faces, true);
        face_usage[base_face_id] = false;

        partial_unfolding.clear();

        // Add the base face as the first element of the partial unfolding path
        // 基準面を部分展開図パスの最初の要素として追加
        partial_unfolding.push_back({
            base_face_id,
            polyhedron.gon_list[base_face_id],
            base_edge_id,
            0.0,    // x: placed at origin
            0.0,    // y: placed at origin
            0.0     // angle: arbitrary for the base face
        });

        // Compute the state of the second face (special case)
        // 2つ目の面の状態を計算（特別なケース）
        FaceState second_face_state = getSecondFaceState();

        // Start the recursive search
        // 再帰探索を開始
        searchPartialUnfoldings(second_face_state, face_usage, jsonl_output);
    }

private:
    // ------------------------------------------------------------------------
    // Private member variables
    // ------------------------------------------------------------------------

    // Polyhedron structure (immutable reference)
    // 多面体構造（不変参照）
    const Polyhedron& polyhedron;

    // ID of the base face (placed at the origin)
    // 基準面のID（原点に配置）
    int base_face_id;

    // ID of the base edge (used for the first rotation)
    // 基準辺のID（最初の回転に使用）
    int base_edge_id;

    // Flag indicating whether y-axis symmetry pruning is enabled
    // y軸対称性枝刈りが有効かどうかを示すフラグ
    bool symmetry_enabled;

    // Flag tracking whether any face center has moved off the y-axis
    // (used only when symmetry_enabled is true)
    // 任意の面の中心がy軸から外れたかを追跡するフラグ
    // （symmetry_enabled が true の時にのみ使用）
    bool y_moved_off_axis;

    // Current partial unfolding path being explored
    // 現在探索中の部分展開図パス
    std::vector<UnfoldedFace> partial_unfolding;

    // ------------------------------------------------------------------------
    // Private helper methods
    // ------------------------------------------------------------------------

    // ------------------------------------------------------------------------
    // getSecondFaceState
    // ------------------------------------------------------------------------
    //
    // Computes the state of the second face after unfolding around the base edge.
    // This is a special case because the first rotation is determined by the
    // base face and base edge placement.
    //
    // 基準辺の周りを展開した後の2つ目の面の状態を計算する。
    // 基準面と基準辺の配置によって最初の回転が決定されるため、これは特別なケース。
    //
    // Guarantee:
    //   - Returns a valid FaceState for the second face
    //   - The second face is adjacent to the base face via the base edge
    //   - Positioned such that the base edge is perpendicular to the x-axis
    //
    // 保証:
    //   - 2つ目の面について有効な FaceState を返す
    //   - 2つ目の面は基準辺を介して基準面に隣接している
    //   - 基準辺がx軸に垂直になるように配置される
    //
    // ------------------------------------------------------------------------
    FaceState getSecondFaceState() {
        int base_edge_pos = polyhedron.getEdgeIndex(base_face_id, base_edge_id);

        // Calculate the sum of diameters of circumscribed circles of all
        // remaining faces (excluding the base face)
        // すべての残りの面（基準面を除く）の外接円の直径の合計を計算
        double remaining_distance = 0.0;
        for (int i = 0; i < polyhedron.num_faces; ++i) {
            if (i != base_face_id) {
                remaining_distance += 2.0 * GeometryUtil::circumradius(polyhedron.gon_list[i]);
            }
        }

        int second_face_id = polyhedron.adj_faces[base_face_id][base_edge_pos];
        int second_edge_id = polyhedron.adj_edges[base_face_id][base_edge_pos];

        double base_face_inradius = GeometryUtil::inradius(polyhedron.gon_list[base_face_id]);
        double second_face_inradius = GeometryUtil::inradius(polyhedron.gon_list[second_face_id]);

        // Place the base edge perpendicular to the x-axis.
        // For a regular-faced polyhedron, the second face's center has y = 0,
        // and its x-coordinate is the sum of the inradii of the base and second faces.
        //
        // 基準辺をx軸に垂直に配置する。
        // 正多面体の場合、2つ目の面の中心はy = 0であり、
        // そのx座標は基準面と2つ目の面の内接円半径の合計となる。
        double second_face_x = base_face_inradius + second_face_inradius;
        double second_face_y = 0.0;

        // From the center of the second face, the base edge is at -180°,
        // so the initial angle is set to -180°.
        //
        // 2つ目の面の中心から見て、基準辺は -180° の位置にあるため、
        // 初期角度は -180° に設定される。
        double second_face_angle = -180.0;

        return {
            second_face_id,
            second_edge_id,
            second_face_x,
            second_face_y,
            second_face_angle,
            remaining_distance,
            symmetry_enabled,
            y_moved_off_axis
        };
    }

    // ------------------------------------------------------------------------
    // backtrackCurrentFace
    // ------------------------------------------------------------------------
    //
    // Removes the currently added face from the partial unfolding path
    // and marks it as unused.
    //
    // 現在追加された面を部分展開図パスから削除し、未使用にマークする。
    //
    // Guarantee:
    //   - Removes the last face from partial_unfolding
    //   - Marks current_face_id as unused in face_usage
    //   - No side effects beyond these modifications
    //
    // 保証:
    //   - partial_unfolding から最後の面を削除
    //   - face_usage で current_face_id を未使用にマーク
    //   - これらの変更以外の副作用はない
    //
    // ------------------------------------------------------------------------
    void backtrackCurrentFace(int current_face_id,
                              std::vector<bool>& face_usage) {
        partial_unfolding.pop_back();
        face_usage[current_face_id] = true;
    }

    // ------------------------------------------------------------------------
    // searchPartialUnfoldings
    // ------------------------------------------------------------------------
    //
    // Recursively searches for partial unfoldings by adding adjacent faces.
    // At each step, checks for potential overlaps and applies pruning heuristics.
    //
    // 隣接面を追加することで部分展開図を再帰的に探索する。
    // 各ステップで潜在的な重なりをチェックし、枝刈りヒューリスティクスを適用する。
    //
    // Input:
    //   state        : State of the face to be added
    //   face_usage   : Tracks which faces are already used (modified in-place)
    //   jsonl_output : Output stream for JSONL records
    //
    // 入力:
    //   state        : 追加する面の状態
    //   face_usage   : すでに使用された面を追跡（その場で変更）
    //   jsonl_output : JSONLレコード用の出力ストリーム
    //
    // Guarantee:
    //   - Explores all valid branches from this state
    //   - Outputs JSONL records when overlap is detected
    //   - Restores face_usage and partial_unfolding upon return (backtracking)
    //   - Applies distance and symmetry pruning to reduce search space
    //
    // 保証:
    //   - この状態からのすべての有効な枝を探索
    //   - 重なりが検出された場合にJSONLレコードを出力
    //   - 戻る際に face_usage と partial_unfolding を復元（バックトラック）
    //   - 探索空間を削減するために距離と対称性の枝刈りを適用
    //
    // ------------------------------------------------------------------------
    void searchPartialUnfoldings(FaceState state,
                                 std::vector<bool>& face_usage,
                                 std::ostream& jsonl_output) {

        int current_face_id = state.face_id;
        int current_face_gon = polyhedron.gon_list[current_face_id];

        // Mark the current face as used
        // 現在の面を使用済みにマーク
        face_usage[current_face_id] = false;

        // Update remaining distance by subtracting the current face's circumradius
        // 現在の面の外接円の直径を減算して残距離を更新
        state.remaining_distance -= 2 * GeometryUtil::circumradius(current_face_gon);

        GeometryUtil::normalizeAngle(state.angle);

        // Add the current face to the partial unfolding path
        // 現在の面を部分展開図パスに追加
        partial_unfolding.push_back({
            current_face_id,
            current_face_gon,
            state.edge_id,
            state.x,
            state.y,
            state.angle
        });

        // Round very small values to zero to avoid floating-point noise
        // 浮動小数点ノイズを避けるために、非常に小さい値を0に丸める
        if (std::fabs(state.x) < 1e-10) state.x = 0.0;
        if (std::fabs(state.y) < 1e-10) state.y = 0.0;

        double distance_from_origin = GeometryUtil::getDistanceFromOrigin(state.x, state.y);

        double base_face_circumradius = GeometryUtil::circumradius(polyhedron.gon_list[base_face_id]);
        double current_face_circumradius = GeometryUtil::circumradius(current_face_gon);

        // Pruning: If the remaining unused faces cannot reach the base face, prune this branch
        // 枝刈り: 残りの未使用面が基準面に到達できない場合、この枝を刈り込む
        if (distance_from_origin > state.remaining_distance
                                 + base_face_circumradius
                                 + current_face_circumradius
                                 + GeometryUtil::buffer) {
            backtrackCurrentFace(current_face_id, face_usage);
            return;
        }

        // Symmetry pruning: If y-axis symmetry is enabled and the face center
        // has moved negative for the first time, prune this branch
        // (a symmetric unfolding exists on the positive side)
        //
        // 対称性枝刈り: y軸対称性が有効で、面の中心が初めて負になった場合、
        // この枝を刈り込む（正の側に対称な展開図が存在する）
        if (state.symmetry_enabled) {
            if (state.y > 0.0) state.y_moved_off_axis = false;
            if (state.y_moved_off_axis && state.y < 0.0) {
                backtrackCurrentFace(current_face_id, face_usage);
                return;
            }
        }

        // Overlap detection: If the circumradii of the base face and the current face
        // are close enough, output this partial unfolding as a candidate
        //
        // 重なり検出: 基準面と現在の面の外接円が十分に近い場合、
        // この部分展開図を候補として出力
        if (distance_from_origin < base_face_circumradius
                                 + current_face_circumradius
                                 + GeometryUtil::buffer) {
            JsonUtil::writeJsonlRecord(
                jsonl_output,
                base_face_id,
                base_edge_id,
                symmetry_enabled,
                partial_unfolding
            );
        }

        // Get the index of the current edge to determine the starting position
        // for exploring adjacent faces
        // 隣接面の探索開始位置を決定するために、現在の辺のインデックスを取得
        int current_edge_pos = polyhedron.getEdgeIndex(current_face_id, state.edge_id);

        double next_face_angle = state.angle;

        // Explore all adjacent faces except the one we came from
        // 来た方向の面を除くすべての隣接面を探索
        for (int i = current_edge_pos + 1; i < current_edge_pos + current_face_gon; ++i) {
            // Incrementally adjust the rotation angle for each adjacent face
            // 各隣接面について回転角度を段階的に調整
            next_face_angle -= 360.0 / static_cast<double>(current_face_gon);
            GeometryUtil::normalizeAngle(next_face_angle);

            int next_face_id = polyhedron.adj_faces[current_face_id][i % current_face_gon];

            // Skip if the adjacent face is already used
            // 隣接面がすでに使用済みの場合はスキップ
            if (!face_usage[next_face_id]) continue;

            int next_edge_id = polyhedron.adj_edges[current_face_id][i % current_face_gon];

            // The distance between the centers of the current and next faces
            // is the sum of their inradii. Since the angle is already computed,
            // use trigonometry to calculate the next face's position.
            //
            // 現在の面と次の面の中心間の距離は、両面の内接円半径の合計である。
            // 角度はすでに計算されているので、三角関数を使用して次の面の位置を計算する。
            double current_inradius = GeometryUtil::inradius(current_face_gon);
            double next_inradius = GeometryUtil::inradius(polyhedron.gon_list[next_face_id]);

            double next_face_x = state.x
                               + (current_inradius + next_inradius)
                               * std::cos(next_face_angle * GeometryUtil::PI / 180.0);
            double next_face_y = state.y
                               + (current_inradius + next_inradius)
                               * std::sin(next_face_angle * GeometryUtil::PI / 180.0);

            FaceState next_state = {
                next_face_id,
                next_edge_id,
                next_face_x,
                next_face_y,
                next_face_angle - 180.0,  // Angle from next face back to current face
                state.remaining_distance,
                state.symmetry_enabled,
                state.y_moved_off_axis
            };

            searchPartialUnfoldings(next_state, face_usage, jsonl_output);
        }

        backtrackCurrentFace(current_face_id, face_usage);
    }
};

#endif  // REORG_ROTATIONAL_UNFOLDING_HPP
