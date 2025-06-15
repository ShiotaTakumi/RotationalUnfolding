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

    // Returns the index of edge_id in adj_edges[face_id].
    int getEdgeIndex(int face_id, int edge_id) const {
        const auto& edges = adj_edges[face_id];
        for (int i = 0; i < static_cast<int>(edges.size()); ++i) {
            if (edges[i] == edge_id) return i;
        }
        return -1;
    }
};

#endif  // POLYHEDRON_HPP
