#ifndef ROTATIONAL_UNFOLDING_IOUTIL_HPP
#define ROTATIONAL_UNFOLDING_IOUTIL_HPP

#include "rotational_unfolding/Polyhedron.hpp"
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>

namespace IOUtil {

// 設定ファイル（.ini）からパスの設定を読み込み、[paths] セクションの値を取得する関数
// 必須キー：adj_path、base_path、raw_path
// Loads path settings from a .ini configuration file,
// reading values from the [paths] section.
// Requires the keys: adj_path, base_path, and raw_path.
inline bool loadPathListIni(const std::string& ini_file, std::string& adj_path, std::string& base_path, std::string& raw_path) {
    std::ifstream infile(ini_file);
    if (!infile) {
        std::cerr << "Error: Cannot open .ini file: " << ini_file << std::endl;
        return false;
    }

    std::string line;

    adj_path.clear(); base_path.clear(); raw_path.clear();

    while (std::getline(infile, line)) {
        if (line.empty() || line[0] == '[' || line[0] == '#' || line[0] == ';') continue;

        std::istringstream iss(line);
        std::string key, eq, value;
        if (!(iss >> key >> eq) || eq != "=") continue;
        std::getline(iss, value);
        value.erase(0, value.find_first_not_of(" \t"));

        if (key == "adj_path") adj_path = value;
        else if (key == "base_path") base_path = value;
        else if (key == "raw_path") raw_path = value;
    }

    if (adj_path.empty() || base_path.empty() || raw_path.empty()) {
        std::cerr << "Error: Missing one or more required keys (adj_path, base_path, raw_path) in the .ini file." << std::endl;
        return false;
    }

    return true;
}

// .adj ファイルから多面体の構造を読み込む関数
// num_faces、gon_list、adj_edges、adj_faces の各メンバを設定する
// Loads a polyhedron structure from an adjacency (.adj) file.
// Fills the members: num_faces, gon_list, adj_edges, and adj_faces.
inline bool loadPolyhedronFromFile(const std::string& adj_path, Polyhedron& poly) {
    std::ifstream file(adj_path);
    if (!file) {
        std::cerr << "Error: Cannot open .adj file: " << adj_path << std::endl;
        return false;
    }

    std::string line;
    int current_face = 0;
    bool hasN = false, hasE = false, hasF = false;

    while (std::getline(file, line)) {
        if (line.rfind("NF", 0) == 0) {
            int nf;
            std::istringstream(line.substr(2)) >> nf;
            poly.num_faces = nf;
            poly.gon_list.resize(nf);
            poly.adj_edges.resize(nf);
            poly.adj_faces.resize(nf);
        } else if (line.rfind("N", 0) == 0) {
            std::istringstream(line.substr(1)) >> poly.gon_list[current_face];
            hasN = true;
        } else if (line.rfind("E", 0) == 0) {
            std::istringstream iss(line.substr(1));
            int e;
            while (iss >> e) poly.adj_edges[current_face].push_back(e);
            hasE = true;
        } else if (line.rfind("F", 0) == 0) {
            std::istringstream iss(line.substr(1));
            int f;
            while (iss >> f) poly.adj_faces[current_face].push_back(f);
            hasF = true;
        }

        // N, E, F の要素を読み込んだら次の面へ
        // Move to the next face after reading all N, E, and F elements.
        if (hasN && hasE && hasF) {
            current_face++;
            hasN = hasE = hasF = false; // リセット / Reset
        }
    }

    return true;
}

// Determines symmetry from filename prefix: a, p, r, or s01–s11.
inline bool isSymmetricFromFilename(const std::string& adj) {
    std::string filename = adj.substr(adj.find_last_of("/\\") + 1);
    if (filename.empty()) return false;

    char head = filename[0];
    if (head == 'a' || head == 'p' || head == 'r') return true;

    if (filename.size() >= 3 && filename[0] == 's') {
        std::string num_part = filename.substr(1, 2);
        try {
            int num = std::stoi(num_part);
            return (1 <= num && num <= 11);
        } catch (...) {
            return false;
        }
    }
    return false;
}

// Loads base face/edge ID pairs from a .base file.
inline bool loadBasePairsFromFile(const std::string& base_path, std::vector<std::pair<int, int>>& base_pairs) {
    std::ifstream infile(base_path);
    if (!infile) {
        std::cerr << "Error: Cannot open base file: " << base_path << std::endl;
        return false;
    }

    int face, edge;
    while (infile >> face >> edge) {
        base_pairs.emplace_back(face, edge);
    }

    return true;
}

} // namespace IOUtil

#endif // ROTATIONAL_UNFOLDING_IOUTIL_HPP
