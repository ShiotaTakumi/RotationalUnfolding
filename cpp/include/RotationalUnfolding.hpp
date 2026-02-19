// ============================================================================
// RotationalUnfolding.hpp
// ============================================================================
//
// What this file does:
//   Implements the core algorithm for exploring path-shaped partial unfoldings
//   of a given polyhedron using rotational unfolding with distance-based
//   and symmetry-based pruning.
//
// このファイルの役割:
//   与えられた多面体に対し、回転展開（rotational unfolding）と
//   距離および対称性に基づく枝刈りを用いて、パス状の部分展開図を探索する
//   中核アルゴリズムを実装する。
//
// Responsibility in the project:
//   - Performs recursive search for path-shaped partial unfoldings
//   - Checks for overlaps between the faces at both ends of the path
//   - Applies distance-based and symmetry-based pruning
//   - Outputs partial unfoldings that may contain overlaps as JSONL records
//   - Does NOT handle file I/O or CLI argument parsing
//
// プロジェクト内での責務:
//   - パス状の部分展開図の再帰的探索を実行
//   - パスの両端に位置する面どうしの重なり判定を行う
//   - 距離および対称性に基づく枝刈りを適用
//   - 重なりを持つ可能性がある部分展開図をJSONLレコードとして出力
//   - ファイルI/OやCLI引数の解析は担当しない
//
// Phase 1 における位置づけ:
//   Core algorithm for Phase 1.
//   Since overlaps between faces are approximated by circumradius intersection,
//   the output may include paths that do not actually overlap.
//   It may also produce isomorphic paths as duplicates.
//   Isomorphic path elimination is done in Phase 2,
//   and exact overlap verification in Phase 3.
//
//   Phase 1の中核アルゴリズム。
//   面どうしの重なりを外接円の交差で近似判定しているため、
//   実際には重ならないパスも含まれうる。
//   また、同型なパスも重複して生成される。
//   同型なパスの除去はPhase 2、厳密な重なり検証はPhase 3で行う。
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
// Explores path-shaped partial unfoldings of a polyhedron.
// Performs a depth-first search starting from a specified
// base face (the face placed on the plane as the starting point)
// and base edge (the edge used as the rotation axis for the first step),
// checking for overlaps between the faces at both ends of the path.
//
// 多面体のパス状の部分展開図を探索する。
// 指定された基準面（展開の起点として平面に置く面）と
// 基準辺（最初の回転軸となる辺）から深さ優先探索を行い、
// パスの両端に位置する面どうしの重なりを判定する。
//
// Responsibility:
//   - Manages the recursive search state
//   - Applies distance-based and symmetry-based pruning
//   - Detects potential overlaps based on circumradius intersection
//   - Outputs candidate partial unfoldings in JSONL format
//
// 責務:
//   - 再帰探索の状態を管理
//   - 距離および対称性に基づく枝刈りを適用
//   - 外接円の交差に基づいて重なりの可能性を判定
//   - 候補となる部分展開図をJSONL形式で出力
//
// Does NOT handle:
//   - Isomorphic partial unfolding elimination (done in Phase 2)
//   - Exact overlap verification (done in Phase 3)
//   - File I/O management
//
// 責務外:
//   - 同型なパス状の部分展開図の除去（Phase 2で実施）
//   - 厳密な重なり検証（Phase 3で実施）
//   - ファイルI/O管理
//
// Algorithm overview:
//   1. Place the base face so that its center is at the origin
//      and the base edge is perpendicular to the positive x-axis
//   2. Recursively add adjacent faces, rotating around shared edges
//   3. Check at each step whether the circumradius of the last face
//      in the path intersects with the circumradius of the base face
//   4. If intersection is detected, output the partial unfolding as a candidate
//      (since the faces may not actually overlap, the search continues)
//   5. Reduce the search space by distance-based and symmetry-based pruning
//
// アルゴリズムの概要:
//   1. 基準面の中心が原点、基準辺がx軸正方向に垂直となるように配置する
//   2. 共有辺を回転軸として、隣接面を再帰的に追加していく
//   3. パスの最終面の外接円が基準面の外接円と交差するかを逐次判定する
//   4. 交差が検出された場合、その部分展開図を候補として出力する
//      （実際には重ならない可能性もあるため、検出後も探索を継続する）
//   5. 距離および対称性に基づく枝刈りで探索空間を削減する
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
    //   base_face         : ID of the base face (the face placed on the plane as the starting point)
    //   base_edge         : ID of the base edge (the edge used as the rotation axis for the first step)
    //   enable_symmetry   : Whether to enable y-axis symmetry-based pruning
    //   y_moved_off_axis  : Whether no face center has yet moved away from y=0
    //                       (used for symmetry pruning; usually same as enable_symmetry)
    //
    // 入力:
    //   poly              : 多面体構造への参照（不変）
    //   base_face         : 基準面のID（展開の起点として平面に置く面）
    //   base_edge         : 基準辺のID（最初の回転軸となる辺）
    //   enable_symmetry   : y軸対称性に基づく枝刈りを有効にするか
    //   y_moved_off_axis  : 面の中心がまだy=0以外の値に移動していないか
    //                       （対称性枝刈りの判定に使用。通常は enable_symmetry と同じ）
    //
    // Guarantee:
    //   - Initializes the search state
    //   - Does not modify the polyhedron structure
    //   - Does not start the search; call runRotationalUnfolding to begin
    //
    // 保証:
    //   - 探索状態を初期化する
    //   - 多面体構造を変更しない
    //   - コンストラクタでは探索を開始しない。探索開始には runRotationalUnfolding を呼ぶ
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
    //   jsonl_output : Output stream for JSONL records
    //                  (one line per candidate path-shaped partial unfolding)
    //
    // 入力:
    //   jsonl_output : JSONLレコード用の出力ストリーム
    //                  （候補となるパス状の部分展開図ごとに1行）
    //
    // Output:
    //   Writes all candidates found during the search as JSONL records
    //   to jsonl_output.
    //
    // 出力:
    //   探索中に見つかったすべての候補をJSONLレコードとして
    //   jsonl_output に書き込む。
    //
    // Guarantee:
    //   - Explores all constructible paths starting from the base face/edge
    //   - Each output record represents a partial unfolding where the circumradii
    //     of the base face and the last face intersect
    //   - Reduces the search space by distance-based and symmetry-based pruning
    //   - Does not modify the polyhedron structure
    //   - May write zero or more JSONL records depending on the polyhedron
    //
    // 保証:
    //   - 基準面・基準辺から始まる、構成可能なすべてのパスを探索する
    //   - 各出力レコードは、基準面と最終面の外接円が交差する部分展開図を表す
    //   - 距離および対称性に基づく枝刈りで探索空間を削減する
    //   - 多面体構造を変更しない
    //   - 多面体に応じて0個以上のJSONLレコードを書き込む
    //
    // ------------------------------------------------------------------------
    void runRotationalUnfolding(std::ostream& jsonl_output) {

        // Initialize array tracking whether each face is used in the path (true = unused, false = used)
        // 各面がパスに使用済みかどうかを管理する配列を初期化（true = 未使用、false = 使用済み）
        std::vector<bool> face_usage(polyhedron.num_faces, true);
        face_usage[base_face_id] = false;

        partial_unfolding.clear();

        // Add the base face as the first element of the path-shaped partial unfolding
        // 基準面をパス状の部分展開図の最初の要素として追加する
        partial_unfolding.push_back({
            base_face_id,
            polyhedron.gon_list[base_face_id],
            base_edge_id,
            0.0,    // x: placed at origin
            0.0,    // y: placed at origin
            0.0     // angle: arbitrary for the base face
        });

        // Compute the state of the second face
        // (derived directly from the initial placement, unlike the 3rd face onward which are computed recursively)
        // 2番目の面の状態を計算する
        // （基準面の初期配置から直接算出するため、再帰的に計算する3番目以降とは処理が異なる）
        FaceState second_face_state = getSecondFaceState();

        // Start the recursive search from the second face
        // 2番目の面から再帰探索を開始する
        searchPartialUnfoldings(second_face_state, face_usage, jsonl_output);
    }

private:
    // ------------------------------------------------------------------------
    // Private member variables
    // ------------------------------------------------------------------------

    // Reference to the polyhedron structure (immutable)
    // 多面体構造への参照（不変）
    const Polyhedron& polyhedron;

    // ID of the base face (the face placed on the plane as the starting point)
    // 基準面のID（展開の起点として平面に置く面）
    int base_face_id;

    // ID of the base edge (the edge used as the rotation axis for the first step)
    // 基準辺のID（最初の回転軸となる辺）
    int base_edge_id;

    // Whether to enable y-axis symmetry-based pruning
    // y軸対称性に基づく枝刈りを有効にするか
    bool symmetry_enabled;

    // Whether no face center has yet moved away from y=0
    // (used for symmetry pruning; usually same as enable_symmetry)
    // 面の中心がまだy=0以外の値に移動していないか
    // （対称性枝刈りの判定に使用。通常は enable_symmetry と同じ）
    bool y_moved_off_axis;

    // Sequence of unfolded faces constituting the current path-shaped partial unfolding
    // 現在探索中のパス状の部分展開図を構成する展開済みの面の列
    std::vector<UnfoldedFace> partial_unfolding;

    // ------------------------------------------------------------------------
    // Private helper methods
    // ------------------------------------------------------------------------

    // ------------------------------------------------------------------------
    // getSecondFaceState
    // ------------------------------------------------------------------------
    //
    // Computes the state of the second face after unfolding around the base edge.
    // Derived directly from the initial placement, unlike the 3rd face onward
    // which are computed recursively.
    //
    // 基準辺を回転軸として展開した後の2番目の面の状態を計算する。
    // 基準面の初期配置から直接算出するため、再帰的に計算する3番目以降とは処理が異なる。
    //
    // Guarantee:
    //   - Returns a FaceState containing the ID, coordinates, angle, and symmetry pruning flags for the second face
    //   - The second face is adjacent to the base face via the base edge
    //   - The base edge is positioned perpendicular to the x-axis
    //
    // 保証:
    //   - 2番目の面のID・座標・角度・対称性枝刈りフラグを含む FaceState を返す
    //   - 2番目の面は基準辺を介して基準面に隣接している
    //   - 基準辺はx軸に垂直になるように配置される
    //
    // ------------------------------------------------------------------------
    FaceState getSecondFaceState() {
        int base_edge_pos = polyhedron.getEdgeIndex(base_face_id, base_edge_id);

        // For distance-based pruning, calculate the sum of diameters of
        // circumscribed circles of all faces excluding the base face
        // 距離に基づく枝刈りのために、基準面を除くすべての面の外接円の直径の合計を計算する
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

        // Place the base edge perpendicular to the positive x-axis.
        // For a convex regular-faced polyhedron, the second face's center has y = 0,
        // and its x-coordinate is the sum of the inradii of the base and second faces.
        //
        // 基準辺をx軸正の方向に垂直に配置する。
        // 整面凸多面体の場合、2番目の面の中心はy = 0であり、
        // そのx座標は基準面と2番目の面の内接円半径の合計となる。
        double second_face_x = base_face_inradius + second_face_inradius;
        double second_face_y = 0.0;

        // The vector from the center of the second face to the center of the base face
        // points in the negative x-direction, and the base edge is perpendicular to this vector.
        // Since angles are measured from the positive x-axis in the range [-180°, 180°],
        // the initial angle is set to -180°.
        //
        // 2番目の面の中心から基準面の中心へ向かうベクトルの方向はx軸負方向であり、
        // 基準辺はこのベクトルに直交する。
        // 角度はx軸正方向を0°とし -180°以上180°以下で表すため、初期角度は -180° とする。
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
