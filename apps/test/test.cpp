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
    // Path to the .adj file (polyhedron adjacency information).
    std::string adj_path;
    // .base ファイル（基準面と基準辺のペアのリスト）へのパス
    // Path to the .base file (base face–edge pairs).
    std::string base_path;
    // 同型な部分展開図も含む生のデータを格納する
    // .ufd ファイル（部分展開図の面どうしのつながりを表す）へのパス
    // Path to the .ufd file (unfolding data representing face-to-face connections)
    // that stores raw unfolding data, including isomorphic ones.
    std::string raw_path;

    // 設定ファイル（.ini）からパスの情報を読み込む
    // Load paths from the configuration (.ini) file.
    if (!IOUtil::loadPathListIni(ini_file, adj_path, base_path, raw_path)) {
        return 1;
    }

    // 読み込んだ多面体の隣接構造を保持するインスタンス
    // Polyhedron instance storing the loaded adjacency structure.
    Polyhedron poly;

    // .adj ファイル（多面体の隣接関係を表す）を読み込む
    // Load the .adj file (polyhedron adjacency information).
    if (!IOUtil::loadPolyhedronFromFile(adj_path, poly)) {
        return 1;
    }

    // 基準面と基準辺のペアのリスト
    // List of base face–edge pairs.
    std::vector<std::pair<int, int>> base_pairs;

    // .base ファイル（基準面と基準辺のペアのリスト）を読み込む
    // Load the .base file (list of base face–edge pairs).
    if (!IOUtil::loadBasePairsFromFile(base_path, base_pairs)) {
        return 1;
    }

    // 回転展開の結果を書き込むための出力ストリーム
    // Output stream for writing the results of the rotational unfolding.
    std::ofstream raw_file(raw_path);

    // 回転展開の実行結果を出力する .ufd ファイル
    // （部分展開図の面どうしのつながりを表す）を開くことができるかの確認
    // Check if the output .ufd file for writing the results of
    // the rotational unfolding (representing face-to-face connections
    // of partial unfoldings) can be opened.
    if (!raw_file) {
        std::cerr << "Error: Cannot open .ufd file: " << raw_path << std::endl;
        return 1;
    }

    // 多面体が対称かどうかを示すフラグ（ファイル名から判定）
    //  Flag indicating whether the polyhedron is symmetric
    // (determined from the filename)
    const bool symmetric = IOUtil::isSymmetricFromFilename(adj_path);
    std::cout << (symmetric ? "Symmetric " : "Asymmetric ") << "polyhedron\n";

    // Run unfolding search
    const int total = base_pairs.size();
    int current = 0;
    for (const auto& [face, edge] : base_pairs) {
        std::cout << (++current) << "/" << total << std::endl;

        RotationalUnfolding search(poly, face, edge, symmetric, symmetric);
        std::stringstream buffer;
        search.searchSequence(buffer);
        raw_file << buffer.str();
        // Flush after each output for safety
        raw_file.flush();
    }

    return 0;
}
