#ifndef UNFOLDING_STATE_HPP
#define UNFOLDING_STATE_HPP

#include <vector>
#include "UnfoldedFace.hpp"  // For UnfoldedFace

// A struct representing the current state of the unfolding
// procesat a recursive step.
struct UnfoldingState {
    // ID of the face currently being placed.
    int face_id;

    // ID of the edge used as the pivot for unfolding
    // from the previous face.
    int edge_id;

    // X-coordinate of the center of the current face.
    double x;

    // Y-coordinate of the center of the current face.
    double y;

    // Orientation angle pointing opposite to the
    // unfolding direction.
    double angle;

    // // A boolean vector indicating whether each face has
    // // not yet been unfolded (true if unused).
    // std::vector<bool> face_usage;

    // // List of faces that have already been unfolded
    // // before the current one.
    // std::vector<UnfoldedFace> unfolding_sequence;

    // Sum of the diameters of the circumscribed circles of
    // all unused faces (including the current face).
    double remaining_distance;

    // Whether symmetric pruning is enabled.
    bool symmetry_enabled;

    // Whether the y-coordinate has ever been non-zero
    // since the base face.
    bool y_moved_off_axis;
};

#endif  // UNFOLDING_STATE_HPP
