#ifndef ROTATIONAL_UNFOLDING_HPP
#define ROTATIONAL_UNFOLDING_HPP

#include "rotational_unfolding/FaceState.hpp"
#include "rotational_unfolding/UnfoldedFace.hpp"
#include "rotational_unfolding/Polyhedron.hpp"
#include "rotational_unfolding/GeometryUtil.hpp"
#include <vector>
#include <iostream>
#include <cmath>
#include <sstream>

// 与えられた多面体と基準面および基準辺を基に、パス状の部分展開図を探索するクラス
// 本クラスでは、各パス状の部分展開図の両端点での重なりチェックも行う
// A class that explores path-shaped partial edge unfoldings of
// a given polyhedron starting from a specified base face and edge.
// This class checks for overlaps at both endpoints of each edge unfolding.
class RotationalUnfolding {
public:
    // コンストラクタ
    // 多面体の情報、基準面、基準辺、立体の対称性を受け取る
    // Constructor
    // Receives the polyhedron data, base face, base edge, and symmetry option
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

    // 回転展開の探索を開始するメソッド
    // 初期状態を設定し、基準面を配置したうえで、再帰処理を呼び出す
    // Method to start the rotational unfolding search.
    // Sets up the initial state, places the base face,
    // and calls the recursive process.
    void runRotationalUnfolding(std::ostream& ufd_output) {

        // 各面が未使用（true）か使用済み（false）かを管理する配列
        // Array tracking whether each face is
        // unused (true) or already used (false).
        std::vector<bool> face_usage(polyhedron.num_faces, true);
        face_usage[base_face_id] = false;

        partial_unfolding.clear();

        // partial_unfolding に最初の面（基準面）を追加する
        // Add the base face as the first element of partial_unfolding
        partial_unfolding.push_back({
            base_face_id,
            polyhedron.gon_list[base_face_id],
            base_edge_id,
            0.0,    // x
            0.0,    // y
            0.0     // angle
        });

        // 2面目だけは、基準面と基準辺を起点にした特別な処理が必要のため別途計算
        // The second face requires a special calculation
        // based on the base face and base edge.
        FaceState second_face_state = getSecondFaceState();

        // 再帰的な探索を開始
        // Start recursive search.
        searchPartialUnfoldings(second_face_state, face_usage, ufd_output);
    }

private:
    // 入力として与えられる多面体の構造体（変更が無いため参照型）
    // Input polyhedron structure
    // (held as a reference since it is not modified).
    const Polyhedron& polyhedron;

    // 初期配置する面（基準面）の番号
    // ID of the base face used for the initial placement.
    int base_face_id;
    // 最初の回転で軸となる辺（基準辺）の番号
    // ID of the base edge used as the rotation axis
    // for the first unfolding step.
    int base_edge_id;

    // y 軸対称性に基づく枝刈りを有効にするかどうかのフラグ
    // Flag indicating whether pruning based on y-axis symmetry is enabled.
    bool symmetry_enabled;
    // 新たに展開した面の中心座標が y 軸上以外に
    // なったことがあるかを管理するフラグ
    // symmetry_enabled が true の時にのみ使用
    // Flag indicating whether the center of any newly unfolded face
    // has deviated from the y-axis.
    // Used only when symmetry_enabled is true.
    bool y_moved_off_axis;

    // 現在、探索している部分展開図に含まれる面の情報の配列
    // Array storing information of faces included
    // in the currently searched partial unfolding.
    std::vector<UnfoldedFace> partial_unfolding;

    // 多面体を基準辺を回転軸として展開したあとの底面
    // （つまり部分展開図の 2 つ目の面）の状態を計算する関数
    // Computes the state of the base face after unfolding
    // the polyhedron around the base edge as the rotation axis
    // (i.e., the second face in the partial unfolding).
    FaceState getSecondFaceState() {
        int base_edge_pos = polyhedron.getEdgeIndex(base_face_id, base_edge_id);

        // 基準面を除いた、残りの全ての面の外接円の直径の合計を計算
        // Calculate the sum of the diameters of the circumscribed circles
        // of all remaining faces, excluding the base face.
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

        // 基準辺は、x 軸に対して垂直に配置する
        // 正多面体を考えているため、second face の中心の y 座標は 0、
        // x 座標は、基準面と second face の半径の合計となる
        // Since we consider a regular-faced polyhedron where the base edge
        // is placed perpendicular to the x-axis, the y-coordinate of the
        // second face's center is 0, and the x-coordinate is the sum of
        // the inradii of the base face and the second face.

        double second_face_x = base_face_inradius + second_face_inradius;
        double second_face_y = 0.0;

        // Second face の中心から見て、基準辺は -180° の位置にあるため、
        // 初期角度は -180° に設定される。
        // From the center of the second face, the base edge is located at -180°,
        // so the initial angle is set to -180°.
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

    // 現在の探索の対象となっている面を部分展開図から取り除き、
    // その面を「未使用」に戻すための関数
    // Function that removes the currently searched face
    // from the partial unfolding and marks it as unused.
    void backtrackCurrentFace(int current_face_id,
                              std::vector<bool>& face_usage) {
        partial_unfolding.pop_back();
        face_usage[current_face_id] = true;
    }

    // 基準面と second face の情報に基づき、部分展開図を再帰的に探索する関数
    // 面を追加する都度に、基準面と新たに追加した面の重なりの有無を確認する
    // Recursively searches for partial unfoldings based on the base face
    // and second face information. At each step of adding a new face,
    // checks for overlaps between the base face and the newly added face.
    void searchPartialUnfoldings(FaceState state,
                                 std::vector<bool>& face_usage,
                                 std::ostream& ufd_output) {

        int current_face_id = state.face_id;
        int current_face_gon = polyhedron.gon_list[current_face_id];

        // 現在の面を使用済みにする
        // Mark the current face as used.
        face_usage[current_face_id] = false;

        // 現在の面の外接円の直径の値を、
        // 部分展開図として使用されていない面の合計値から減算する
        // Subtract the diameter of the current face's circumscribed circle
        // from the total diameter of the unused faces in the partial unfolding.
        state.remaining_distance -= 2 * GeometryUtil::circumradius(current_face_gon);

        GeometryUtil::normalizeAngle(state.angle);

        // 現在の面を部分展開図に追加する
        // Add the current face to the partial unfolding.
        partial_unfolding.push_back({
            current_face_id,
            current_face_gon,
            state.edge_id,
            state.x,
            state.y,
            state.angle
        });

        // 数値誤差を防ぐため、非常に小さい値を 0 に丸める
        // Avoid floating-point noise by rounding near-zero values to 0.
        if (std::fabs(state.x) < 1e-10) state.x = 0.0;
        if (std::fabs(state.y) < 1e-10) state.y = 0.0;

        double distance_from_origin = GeometryUtil::getDistanceFromOrigin(state.x, state.y);

        // 基準面の外接円の半径
        // Circumradius of the base face
        double base_face_circumradius = GeometryUtil::circumradius(polyhedron.gon_list[base_face_id]);
        // 現在の面の外接円の半径
        // Circumradius of the current face
        double current_face_circumradius = GeometryUtil::circumradius(current_face_gon);

        // 未使用の面だけでは基準面まで到達できない場合、枝刈りを行う
        // 数値誤差による誤判定を防ぐため、バッファーを加えて判定する
        // Prune the search if the remaining unused faces alone
        // cannot reach the base face.
        // A buffer is added to prevent misjudgment due to numerical errors.
        if (distance_from_origin > state.remaining_distance
                                 + base_face_circumradius
                                 + current_face_circumradius
                                 + GeometryUtil::buffer) {
            backtrackCurrentFace(current_face_id, face_usage);
            return;
        }

        // 多面体が対称性を持つ場合、y 軸方向の対称性に基づいて枝刈りを行う
        // 面の中心 y 座標が初めて 0 から変化し、負の値となった場合には、
        // 正の側に対称な展開図が既に存在しているため、探索を打ち切る
        // If the polyhedron has symmetry, prune the search based on y-axis symmetry.
        // When the face center’s y-coordinate first deviates from 0 and becomes negative,
        // a symmetric unfolding exists on the positive side, so the search is pruned.
        if (state.symmetry_enabled) {
            if (state.y > 0.0) state.y_moved_off_axis = false;
            if (state.y_moved_off_axis && state.y < 0.0) {
                backtrackCurrentFace(current_face_id, face_usage);
                return;
            }
        }

        // 基準面と現在の面の外接円が重なる場合、現状の部分展開図の
        // 両端に位置する面が重なる可能性があるとして出力をする
        // If the circumscribed circles of the base face and the current face overlap,
        // output the current partial unfolding as it may indicate an overlap
        // between the both end-faces.
        if (distance_from_origin < base_face_circumradius
                                 + current_face_circumradius
                                 + GeometryUtil::buffer) {
            ufd_output << partial_unfolding.size() << " ";
            for (const auto& f : partial_unfolding) {
                ufd_output << f.gon << " "
                          << f.edge_id << " "
                          << f.face_id << " "
                          << f.x << " "
                          << f.y << " "
                          << f.angle << " ";
            }
            ufd_output << "\n";
        }

        // 隣接する面を探索するため、現在の辺の位置を取得する
        // Get the index of the current edge to determine
        // the starting position for exploring adjacent faces.
        int current_edge_pos = polyhedron.getEdgeIndex(current_face_id, state.edge_id);

        double next_face_angle = state.angle;

        // 一つ前の面を除き、すべての隣接する面に対して探索する
        // Search all adjacent faces except the one we came from.
        for (int i = current_edge_pos + 1; i < current_edge_pos + current_face_gon; ++i) {
            // 隣接する各面を探索するため、回転角度を順次ずらす
            // Incrementally adjust the rotation angle to search each adjacent face.
            next_face_angle -= 360.0 / static_cast<double>(current_face_gon);
            GeometryUtil::normalizeAngle(next_face_angle);

            int next_face_id = polyhedron.adj_faces[current_face_id][i % current_face_gon];

            // 隣接する面がすでに使用済みの場合はスキップ
            // Skip if the adjacent face is already used.
            if (!face_usage[next_face_id]) continue;

            int next_edge_id = polyhedron.adj_edges[current_face_id][i % current_face_gon];

            // 現在の面と次の面の中心間の距離は、両面の内接円の半径の合計となる
            // 中心間の角度は計算済みであるため、三角関数を用いて次の面の座標位置を計算する
            // The distance between the centers of the current face and the next face
            // is the sum of their inradii. Since the angle between the centers has
            // already been calculated, the coordinates of the next face are computed
            // using trigonometric functions.

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
                next_face_angle - 180.0,
                state.remaining_distance,
                state.symmetry_enabled,
                state.y_moved_off_axis
            };

            searchPartialUnfoldings(next_state, face_usage, ufd_output);
        }

        backtrackCurrentFace(current_face_id, face_usage);
    }
};

#endif  // ROTATIONAL_UNFOLDING_HPP
