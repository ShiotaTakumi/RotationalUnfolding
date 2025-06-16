#ifndef ROTATIONAL_UNFOLDING_HPP
#define ROTATIONAL_UNFOLDING_HPP

#include "Polyhedron.hpp"
#include "UnfoldingState.hpp"
#include "UnfoldedFace.hpp"
#include "GeometryUtil.hpp"
#include <vector>
#include <iostream>
#include <cmath>

class RotationalUnfolding {
public:
    RotationalUnfolding(const Polyhedron& poly, int base_face, int base_edge, bool enable_symmetry, bool y_moved_off_axis)
    : polyhedron(poly),
      base_face_id(base_face),
      base_edge_id(base_edge),
      symmetry_enabled(enable_symmetry),
      y_moved_off_axis(y_moved_off_axis)
      {
        setupInitialState();
      }

    void searchSequence() {
        std::vector<bool> face_usage(polyhedron.num_faces, true);
        face_usage[base_face_id] = false;

        std::vector<UnfoldedFace> unfolding_sequence;
        unfolding_sequence.push_back({
            base_face_id,
            polyhedron.gon_list[base_face_id],
            base_edge_id,
            0.0,
            0.0,
            0.0
        });

        searchUnfoldingSequence(initial_state, face_usage, unfolding_sequence);
    }

private:
    const Polyhedron& polyhedron;
    int base_face_id;
    int base_edge_id;
    bool symmetry_enabled;
    bool y_moved_off_axis;
    UnfoldingState initial_state;

    void setupInitialState() {
        int base_edge_pos = polyhedron.getEdgeIndex(base_face_id, base_edge_id);

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

        double next_face_x = base_face_inradius + next_face_inradius;
        double next_face_y = 0.0;
        double next_face_angle = -180.0;

        initial_state = {
            next_face_id,
            next_edge_id,
            next_face_x,
            next_face_y,
            next_face_angle,
            remaining_distance,
            symmetry_enabled,
            y_moved_off_axis
        };
    }

    void searchUnfoldingSequence(UnfoldingState state,
                                 const std::vector<bool>& face_usage,
                                 const std::vector<UnfoldedFace>& unfolding_sequence) {
        int current_face_id = state.face_id;
        int current_face_gon = polyhedron.gon_list[current_face_id];

        std::vector<bool> face_usage_copy = face_usage;
        std::vector<UnfoldedFace> unfolding_sequence_copy = unfolding_sequence;

        face_usage_copy[current_face_id] = false;
        state.remaining_distance -= 2 * GeometryUtil::circumradius(current_face_gon);
        GeometryUtil::normalizeAngle(state.angle);

        unfolding_sequence_copy.push_back({
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

        if (distance_from_origin > state.remaining_distance + base_face_circumradius + current_face_circumradius + GeometryUtil::buffer)
            return;

        if (state.symmetry_enabled) {
            if (state.y > 0.0) state.y_moved_off_axis = false;
            if (state.y_moved_off_axis && state.y < 0.0) return;
        }

        if (distance_from_origin < base_face_circumradius + current_face_circumradius + GeometryUtil::buffer) {
            std::cout << unfolding_sequence_copy.size() << " ";
            for (const auto& f : unfolding_sequence_copy) {
                std::cout << f.gon << " "
                          << f.edge_id << " "
                          << f.face_id << " "
                          << f.x << " "
                          << f.y << " "
                          << f.angle << " ";
            }
            std::cout << std::endl;
        }

        int current_edge_pos = polyhedron.getEdgeIndex(current_face_id, state.edge_id);
        double next_face_angle = state.angle;

        for (int i = current_edge_pos + 1; i < current_edge_pos + current_face_gon; ++i) {
            next_face_angle -= 360.0 / static_cast<double>(current_face_gon);
            GeometryUtil::normalizeAngle(next_face_angle);

            int next_face_id = polyhedron.adj_faces[current_face_id][i % current_face_gon];
            int next_edge_id = polyhedron.adj_edges[current_face_id][i % current_face_gon];
            if (!face_usage_copy[next_face_id]) continue;

            double current_inradius = GeometryUtil::inradius(current_face_gon);
            double next_inradius = GeometryUtil::inradius(polyhedron.gon_list[next_face_id]);

            double next_face_x = state.x + (current_inradius + next_inradius) * std::cos(next_face_angle * GeometryUtil::PI / 180.0);
            double next_face_y = state.y + (current_inradius + next_inradius) * std::sin(next_face_angle * GeometryUtil::PI / 180.0);

            UnfoldingState next_state = {
                next_face_id,
                next_edge_id,
                next_face_x,
                next_face_y,
                next_face_angle - 180.0,
                state.remaining_distance,
                state.symmetry_enabled,
                state.y_moved_off_axis
            };

            searchUnfoldingSequence(next_state, face_usage_copy, unfolding_sequence_copy);
        }
    }
};

#endif  // ROTATIONAL_UNFOLDING_HPP