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
    bool symmetric;
    if (!IOUtil::loadPolyhedronFromIni(argv[1], poly, symmetric)) {
        std::cerr << "Failed to load polyhedron data from ini file." << std::endl;
        return 1;
    }

    std::vector<std::pair<int, int>> base_pairs;
    if (!IOUtil::loadBasePairsFromIni(argv[1], base_pairs)) {
        std::cerr << "Failed to load base face/edge pairs." << std::endl;
        return 1;
    }

    std::string output_path;
    if (!IOUtil::loadOutputPathFromIni(argv[1], output_path)) {
        std::cerr << "Failed to load output path from ini file." << std::endl;
        return 1;
    }

    std::ofstream out_file(output_path);
    int current = 0, total = base_pairs.size();
    std::cout << (symmetric ? "Symmetric " : "Asymmetric ") << "polyhedron" << std::endl;
    for (const auto& [face, edge] : base_pairs) {
        std::cout << ++current << "/" << total << std::endl;

        RotationalUnfolding search(poly, face, edge, symmetric, symmetric);
        std::stringstream buffer;
        search.searchSequence(buffer);
        out_file << buffer.str();
        out_file.flush();
    }

    return 0;
}
