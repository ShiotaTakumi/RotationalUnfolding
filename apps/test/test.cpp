#include "rotational_unfolding/RotationalUnfolding.hpp"
#include "rotational_unfolding/IOUtil.hpp"

#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

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

    std::vector<std::pair<int, int>> base_pairs;
    if (!IOUtil::loadBasePairsFromIni(argv[1], base_pairs)) {
        std::cerr << "Failed to load base face/edge pairs." << std::endl;
        return 1;
    }

    for (const auto& [face, edge] : base_pairs) {
        RotationalUnfolding search(poly, face, edge, true, true);
        std::stringstream buffer;
        search.searchSequence(buffer);
        std::cout << buffer.str();
    }

    return 0;
}
