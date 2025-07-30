#ifndef ROTATIONAL_UNFOLDING_HPP
#define ROTATIONAL_UNFOLDING_HPP

#include "Polyhedron.hpp"
#include "FaceState.hpp"
#include "UnfoldedFace.hpp"
#include "GeometryUtil.hpp"
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
    // 初期状態を設定し、基準面を配置したうえで、再起処理を呼び出す
    // Method to start the rotational unfolding search.
    // Sets up the initial state, places the base face,
    // and calls the recursive process.
    void runRotationalUnfolding(std::ostream& ufd_output) {

        // 各面が未使用（true）か使用済み（false）かを管理する配列
        // Array tracking whether each face is
        // unused (true) or already used (false).
        std::vector<bool> face_usage(polyhedron.num_faces, true);
        face_usage[base_face_id] = false;

        // unfolding_sequence を空にする
        // Clear unfolding_sequence to ensure it is empty
        unfolding_sequence.clear();

        // unfolding_sequence に最初の面（基準面）を追加する
        // Add the base face as the first element of unfolding_sequence
        unfolding_sequence.push_back({
            base_face_id,
            polyhedron.gon_list[base_face_id],
            base_edge_id,
            0.0,    // x
            0.0,    // y
            0.0     // angle
        });

        FaceState initial_state = setupInitialState();
        searchPartialUnfoldings(initial_state, face_usage, ufd_output);
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
    // in the currently explored partial unfolding.
    std::vector<UnfoldedFace> unfolding_sequence;

    // Computes the initial state after rotating the polyhedron
    // around the base edge used as the unfolding axis.
    FaceState setupInitialState() {
        int base_edge_pos = polyhedron.getEdgeIndex(base_face_id, base_edge_id);

        // Compute initial total remaining radius distance,
        // excluding the base face.
        double remaining_distance = 0.0;
        for (int i = 0; i < polyhedron.num_faces; ++i) {
            if (i != base_face_id) {
                remaining_distance += 2.0 * GeometryUtil::circumradius(polyhedron.gon_list[i]);
            }
        }

        int next_face_id = polyhedron.adj_faces[base_face_id][base_edge_pos];
        int next_edge_id = polyhedron.adj_edges[base_face_id][base_edge_pos];

        double base_face_inradius = GeometryUtil::inradius(polyhedron.gon_list[base_face_id]);
        double next_face_inradius = GeometryUtil::inradius(polyhedron.gon_list[next_face_id]);

        // Since the base edge is perpendicular to the x-axis,
        // the center of the next face lies on the x-axis.
        // The x-coordinate is the sum of the inradii of the
        // base face and the next face.
        double next_face_x = base_face_inradius + next_face_inradius;
        double next_face_y = 0.0;
        // The base edge lies at 0° from the base face center,
        // but appears at -180° from the next face center,
        // so the initial angle is set to -180°.
        double next_face_angle = -180.0;

        FaceState initial_state = {
            next_face_id,
            next_edge_id,
            next_face_x,
            next_face_y,
            next_face_angle,
            remaining_distance,
            symmetry_enabled,
            y_moved_off_axis
        };

        return initial_state;
    }

    // Recursively searches for path-shape edge unfoldings
    // based on the initial state, checking for overlap along
    // the way and applying symmetry pruning if enabled.
    void searchPartialUnfoldings(FaceState state,
                                 std::vector<bool>& face_usage,
                                 std::ostream& ufd_output) {
        int current_face_id = state.face_id;
        int current_face_gon = polyhedron.gon_list[current_face_id];

        face_usage[current_face_id] = false;
        state.remaining_distance -= 2 * GeometryUtil::circumradius(current_face_gon);
        GeometryUtil::normalizeAngle(state.angle);

        unfolding_sequence.push_back({
            current_face_id,
            current_face_gon,
            state.edge_id,
            state.x,
            state.y,
            state.angle
        });

        double base_face_circumradius = GeometryUtil::circumradius(polyhedron.gon_list[base_face_id]);
        double current_face_circumradius = GeometryUtil::circumradius(current_face_gon);

        if (std::fabs(state.x) < 1e-10) state.x = 0.0;
        if (std::fabs(state.y) < 1e-10) state.y = 0.0;

        double distance_from_origin = GeometryUtil::getDistanceFromOrigin(state.x, state.y);

        // Prune if the remaining faces are insufficient to
        // reach the base face.
        if (distance_from_origin > state.remaining_distance + base_face_circumradius + current_face_circumradius + GeometryUtil::buffer) {
            unfolding_sequence.pop_back();
            face_usage[current_face_id] = true;
            return;
        }

        // Prune based on y-axis symmetry.
        if (state.symmetry_enabled) {
            if (state.y > 0.0) state.y_moved_off_axis = false;
            if (state.y_moved_off_axis && state.y < 0.0) {
                unfolding_sequence.pop_back();
                face_usage[current_face_id] = true;
                return;
            }
        }

        // If the circumscribed circles of the base face and
        // the current face overlap, output the current
        // path-shape edge unfolding as a potential overlap case.
        if (distance_from_origin < base_face_circumradius + current_face_circumradius + GeometryUtil::buffer) {
            ufd_output << unfolding_sequence.size() << " ";
            for (const auto& f : unfolding_sequence) {
                ufd_output << f.gon << " "
                          << f.edge_id << " "
                          << f.face_id << " "
                          << f.x << " "
                          << f.y << " "
                          << f.angle << " ";
            }
            ufd_output << std::endl;
        }

        int current_edge_pos = polyhedron.getEdgeIndex(current_face_id, state.edge_id);
        double next_face_angle = state.angle;

        // Continue recursive search as long as adjacent faces are available
        for (int i = current_edge_pos + 1; i < current_edge_pos + current_face_gon; ++i) {
            next_face_angle -= 360.0 / static_cast<double>(current_face_gon);
            GeometryUtil::normalizeAngle(next_face_angle);

            int next_face_id = polyhedron.adj_faces[current_face_id][i % current_face_gon];
            int next_edge_id = polyhedron.adj_edges[current_face_id][i % current_face_gon];
            if (!face_usage[next_face_id]) continue;

            double current_inradius = GeometryUtil::inradius(current_face_gon);
            double next_inradius = GeometryUtil::inradius(polyhedron.gon_list[next_face_id]);

            // The distance between the centers of the current
            //  face and the next face is the sum of their
            // inradii. Since the angle is known, the position
            // is computed using trigonometric functions.
            double next_face_x = state.x + (current_inradius + next_inradius) * std::cos(next_face_angle * GeometryUtil::PI / 180.0);
            double next_face_y = state.y + (current_inradius + next_inradius) * std::sin(next_face_angle * GeometryUtil::PI / 180.0);

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

        // Backtrack
        unfolding_sequence.pop_back();
        face_usage[current_face_id] = true;
    }
};

#endif  // ROTATIONAL_UNFOLDING_HPP