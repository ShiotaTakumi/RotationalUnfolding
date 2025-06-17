#ifndef ROTATIONAL_UNFOLDING_HPP
#define ROTATIONAL_UNFOLDING_HPP

#include "Polyhedron.hpp"
#include "UnfoldingState.hpp"
#include "UnfoldedFace.hpp"
#include "GeometryUtil.hpp"
#include <vector>
#include <iostream>
#include <cmath>
#include <sstream>

// A class that explores path-shape partial edge unfolding
// starting from a specified face and edge of a polyhedron,
// and checks for overlap at both endpoints of each path.
class RotationalUnfolding {
public:
    // Constructor. Prepares the path-shape edge unfolding
    // search from the specified base face and edge.
    RotationalUnfolding(const Polyhedron& poly, int base_face, int base_edge, bool enable_symmetry, bool y_moved_off_axis)
    : polyhedron(poly),
      base_face_id(base_face),
      base_edge_id(base_edge),
      symmetry_enabled(enable_symmetry),
      y_moved_off_axis(y_moved_off_axis)
      {
        setupInitialState();
      }

    // Entry point for launching the recursive search
    // for path-shape edge unfoldings. Internally sets up
    // the first face and delegates to the core search logic.
    void searchSequence(std::ostream& out) {
        std::vector<bool> face_usage(polyhedron.num_faces, true);
        face_usage[base_face_id] = false;

        unfolding_sequence.clear();
        // The base face is placed with its center at (0, 0),
        // and the base edge is perpendicular to the x-axis
        // and lies in the x > 0.
        unfolding_sequence.push_back({
            base_face_id,
            polyhedron.gon_list[base_face_id],
            base_edge_id,
            0.0,    // x
            0.0,    // y
            0.0     // angle
        });

        searchUnfoldingSequence(initial_state, face_usage, out);
    }

private:
    // Reference to the input polyhedron structure.
    const Polyhedron& polyhedron;
    // ID of the initial base face used to begin the unfolding.
    int base_face_id;
    // ID of the edge on the base face used as the rotation
    // axis to initiate unfolding.
    int base_edge_id;
    // Whether pruning based on symmetry with respect to
    // the y-axis is enabled during the search.
    bool symmetry_enabled;
    // Whether any face has deviated from the y-axis (y ≠ 0)
    // since the base face.
    bool y_moved_off_axis;
    // Initial state of the recursive unfolding process,
    // derived from the face that becomes the new base
    // when rotated around the base edge of the base face.
    UnfoldingState initial_state;
    // Array storing the current path-shape edge unfolding
    // sequence.
    std::vector<UnfoldedFace> unfolding_sequence;

    // Computes the initial state after rotating the polyhedron
    // around the base edge used as the unfolding axis.
    void setupInitialState() {
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

    // Recursively searches for path-shape edge unfoldings
    // based on the initial state, checking for overlap along
    // the way and applying symmetry pruning if enabled.
    void searchUnfoldingSequence(UnfoldingState state,
                                 std::vector<bool>& face_usage,
                                 std::ostream& out) {
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
            out << unfolding_sequence.size() << " ";
            for (const auto& f : unfolding_sequence) {
                out << f.gon << " "
                          << f.edge_id << " "
                          << f.face_id << " "
                          << f.x << " "
                          << f.y << " "
                          << f.angle << " ";
            }
            out << std::endl;
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

            searchUnfoldingSequence(next_state, face_usage, out);
        }

        // Backtrack
        unfolding_sequence.pop_back();
        face_usage[current_face_id] = true;
    }
};

#endif  // ROTATIONAL_UNFOLDING_HPP