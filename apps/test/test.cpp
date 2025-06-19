#include "rotational_unfolding/RotationalUnfolding.hpp"
#include "rotational_unfolding/IOUtil.hpp"

#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " path_list.ini" << std::endl;
        return 1;
    }

    const std::string ini_path = argv[1];

    // Load paths from ini file
    std::string data_path, base_path, raw_path;
    if (!IOUtil::loadPathListIni(ini_path, data_path, base_path, raw_path)) {
        std::cerr << "Failed to read required paths from ini file." << std::endl;
        return 1;
    }

    // Load polyhedron from data_path (.adj)
    Polyhedron poly;
    if (!IOUtil::loadPolyhedronFromFile(data_path, poly)) {
        std::cerr << "Failed to load polyhedron from .adj file." << std::endl;
        return 1;
    }

    // Determine symmetry from filename
    const bool symmetric = IOUtil::isSymmetricFromFilename(data_path);
    std::cout << (symmetric ? "Symmetric " : "Asymmetric ") << "polyhedron" << std::endl;

    // Load base face/edge pairs
    std::vector<std::pair<int, int>> base_pairs;
    if (!IOUtil::loadBasePairsFromFile(base_path, base_pairs)) {
        std::cerr << "Failed to load base face/edge pairs from .base file." << std::endl;
        return 1;
    }

    // Prepare output file stream
    std::ofstream out_file(raw_path);
    if (!out_file) {
        std::cerr << "Error: Cannot open output file: " << raw_path << std::endl;
        return 1;
    }

    // Run unfolding search
    const int total = base_pairs.size();
    int current = 0;
    for (const auto& [face, edge] : base_pairs) {
        std::cout << (++current) << "/" << total << std::endl;

        RotationalUnfolding search(poly, face, edge, symmetric, symmetric);
        std::stringstream buffer;
        search.searchSequence(buffer);
        out_file << buffer.str();
        // Flush after each output for safety
        out_file.flush();
    }

    return 0;
}
