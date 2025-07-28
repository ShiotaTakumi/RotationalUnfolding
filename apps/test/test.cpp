#include "rotational_unfolding/RotationalUnfolding.hpp"
#include "rotational_unfolding/IOUtil.hpp"

#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

int main(int argc, char* argv[]) {
    // 設定ファイル（.ini）がコマンドライン引数で
    // 指定されていない場合のエラー
    // Error if the configuration file is not specified
    // as a command-line argument
    if (argc < 2) {
        std::cerr << "Error: Please provide the configuration file path_list.ini as the first argument." << std::endl;
        return 1;
    }

    const std::string ini_file = argv[1];

    // .adj ファイル（多面体の隣接関係を表す）へのパス
    // Path to the .adj file (polyhedron adjacency information)
    std::string adj_path;
    // .base ファイル（展開の起点とする面と頂点のペアを格納）へのパス
    // Path to the .base file (base face–edge pairs)
    std::string base_path;
    // 同型な部分展開図も含む生のデータを格納する
    // .ufd ファイル（部分展開図の面どうしのつながりを表す）へのパス
    // Path to the .ufd file (unfolding data representing face-to-face connections)
    // that stores raw unfolding data, including isomorphic ones
    std::string raw_path;

    // 設定ファイル（.ini）からパスの情報を読み込む
    // Load paths from the configuration (.ini) file.
    if (!IOUtil::loadPathListIni(ini_file, adj_path, base_path, raw_path)) {
        return 1;
    }

    // Load polyhedron from adj_path (.adj)
    Polyhedron poly;
    if (!IOUtil::loadPolyhedronFromFile(adj_path, poly)) {
        std::cerr << "Failed to load polyhedron from .adj file." << std::endl;
        return 1;
    }

    // Determine symmetry from filename
    const bool symmetric = IOUtil::isSymmetricFromFilename(adj_path);
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
