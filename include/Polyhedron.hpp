#ifndef POLYHEDRON_HPP
#define POLYHEDRON_HPP

#include <vector>

// A struct representing the structure of a polyhedron.
struct Polyhedron {
    // Number of faces in the polyhedron.
    int num_faces;

    // Number of edges (gon) for each face.
    std::vector<int> gon_list;

    // List of edge IDs per face.
    // Stored in counterclockwise order with respect to the outward normal.
    std::vector<std::vector<int>> adj_edges;

    // List of adjacent face IDs per face.
    // Aligned with adj_edges.
    std::vector<std::vector<int>> adj_faces;
};

#endif  // POLYHEDRON_HPP
