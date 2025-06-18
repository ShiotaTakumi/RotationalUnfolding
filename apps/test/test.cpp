#include "rotational_unfolding/RotationalUnfolding.hpp"
#include "rotational_unfolding/IOUtil.hpp"

#include <sstream>
#include <iostream>
#include <fstream>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " unfold_config.ini" << std::endl;
        return 1;
    }

    Polyhedron poly;
    if (!IOUtil::loadPolyhedronFromIni(argv[1], poly)) {
        std::cerr << "Failed to load polyhedron data from ini file." << std::endl;
        return 1;
    }

    int base_face_id; std::cin >> base_face_id;
    int base_edge_id; std::cin >> base_edge_id;
    bool enable_symmetry = true;
    bool y_moved_off_axis = true;

    RotationalUnfolding search(poly, base_face_id, base_edge_id, enable_symmetry, y_moved_off_axis);
    std::stringstream buffer;
    search.searchSequence(buffer);
    std::cout << buffer.str();

    return 0;
}
