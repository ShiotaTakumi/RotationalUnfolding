#ifndef UNFOLDED_FACE_HPP
#define UNFOLDED_FACE_HPP

// A struct that stores information of a face after
// it has been unfolded in the plane.
struct UnfoldedFace {
    // ID of the face.
    int face_id;

    // Number of edges (gon) of the face.
    int gon;

    // ID of the edge that is connected to the previous unfolded face.
    int edge_id;

    // X-coordinate of the face center in the unfolding.
    double x;

    // Y-coordinate of the face center in the unfolding.
    double y;

    // Orientation angle (in degrees) from the center of
    // this face to the center of the previously unfolded face.
    double angle;
};

#endif  // UNFOLDED_FACE_HPP
