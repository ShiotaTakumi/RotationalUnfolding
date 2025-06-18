#ifndef ROTATIONAL_UNFOLDING_IOUTIL_HPP
#define ROTATIONAL_UNFOLDING_IOUTIL_HPP

#include "rotational_unfolding/Polyhedron.hpp"
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <filesystem>

namespace IOUtil {

inline bool loadAdjacencyFile(const std::string& filepath, Polyhedron& poly) {
    std::ifstream file(filepath);
    if (!file) {
        std::cerr << "Error: Cannot open file " << filepath << std::endl;
        return false;
    }

    std::string line;
    int current_face = -1;

    while (std::getline(file, line)) {
        if (line.rfind("NF", 0) == 0) {
            int nf;
            std::istringstream(line.substr(2)) >> nf;
            poly.num_faces = nf;
            poly.gon_list.resize(nf);
            poly.adj_edges.resize(nf);
            poly.adj_faces.resize(nf);
        } else if (line.rfind("# --- Face", 0) == 0) {
            current_face++;
        } else if (line.rfind("N", 0) == 0) {
            std::istringstream(line.substr(1)) >> poly.gon_list[current_face];
        } else if (line.rfind("E", 0) == 0) {
            std::istringstream iss(line.substr(1));
            int e;
            while (iss >> e) poly.adj_edges[current_face].push_back(e);
        } else if (line.rfind("F", 0) == 0) {
            std::istringstream iss(line.substr(1));
            int f;
            while (iss >> f) poly.adj_faces[current_face].push_back(f);
        }
    }

    return true;
}

inline bool loadPolyhedronFromPath(const std::string& base_path, const std::string& category, const std::string& file, Polyhedron& poly) {
    std::string path = base_path + "/polyhedron/" + category + "/adjacent/" + file + ".adj";
    return loadAdjacencyFile(path, poly);
}


inline bool loadPolyhedronFromIni(const std::string& ini_path, Polyhedron& poly) {
    std::ifstream infile(ini_path);
    if (!infile) {
        std::cerr << "Error: Cannot open config file: " << ini_path << std::endl;
        return false;
    }

    std::string base_path, category, file;
    std::string line;
    while (std::getline(infile, line)) {
        if (line.empty() || line[0] == '#' || line[0] == '[') continue;

        std::istringstream iss(line);
        std::string key, eq, value;
        if (!(iss >> key >> eq) || eq != "=") continue;
        std::getline(iss, value);
        value.erase(0, value.find_first_not_of(" \t"));

        if (key == "base_path") {
            base_path = value;
        } else if (key == "category") {
            category = value;
        } else if (key == "file") {
            file = value;
        }
    }

    if (base_path.empty() || category.empty() || file.empty()) {
        std::cerr << "Error: Missing fields in config file." << std::endl;
        return false;
    }

    return loadPolyhedronFromPath(base_path, category, file, poly);
}

inline bool parseIniFile(const std::string& ini_path, std::string& base_path, std::string& category, std::string& file) {
    std::ifstream infile(ini_path);
    if (!infile) {
        std::cerr << "Error: Cannot open config file: " << ini_path << std::endl;
        return false;
    }

    std::string line;
    while (std::getline(infile, line)) {
        if (line.empty() || line[0] == '[') continue;

        std::istringstream iss(line);
        std::string key, eq, value;
        if (!(iss >> key >> eq) || eq != "=") continue;
        std::getline(iss, value);
        value.erase(0, value.find_first_not_of(" \t"));

        if (key == "base_path") {
            base_path = value;
        } else if (key == "category") {
            category = value;
        } else if (key == "file") {
            file = value;
        }
    }

    return !(base_path.empty() || category.empty() || file.empty());
}

inline bool loadBasePairsFromIni(const std::string& ini_path, std::vector<std::pair<int, int>>& base_pairs) {
    std::string base_path, category, file;
    if (!parseIniFile(ini_path, base_path, category, file)) {
        return false;
    }

    std::string base_file = base_path + "/polyhedron/" + category + "/base/" + file + ".base";
    std::ifstream infile(base_file);
    if (!infile) {
        std::cerr << "Error: Cannot open base file: " << base_file << std::endl;
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
