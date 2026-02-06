// ============================================================================
// IOUtil.hpp
// ============================================================================
//
// What this file does:
//   Provides utility functions for loading polyhedron data from input files
//   (.adj and .base formats).
//
// このファイルの役割:
//   入力ファイル（.adj および .base 形式）から多面体データを読み込む
//   ユーティリティ関数を提供する。
//
// Responsibility in the project:
//   - Parses .adj files to construct Polyhedron structures
//   - Parses .base files to load base face-edge pairs
//   - Determines symmetry based on filename conventions
//   - Does NOT handle output or unfolding logic
//
// プロジェクト内での責務:
//   - .adj ファイルをパースして Polyhedron 構造を構築
//   - .base ファイルをパースして基準面・辺のペアを読み込み
//   - ファイル名の規約に基づいて対称性を判定
//   - 出力や展開ロジックは担当しない
//
// Phase 1 における位置づけ:
//   Input layer for loading polyhedron data before the search begins.
//   Phase 1では、探索開始前に多面体データを読み込む入力層として機能する。
//
// ============================================================================

#ifndef REORG_IOUTIL_HPP
#define REORG_IOUTIL_HPP

#include "Polyhedron.hpp"
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>

namespace IOUtil {

// ============================================================================
// Input File Parsers
// ============================================================================

// ----------------------------------------------------------------------------
// loadPolyhedronFromFile
// ----------------------------------------------------------------------------
//
// Input:
//   adj_path : Path to the .adj file (polyhedron adjacency data)
//   poly     : Reference to a Polyhedron structure to be filled
//
// 入力:
//   adj_path : .adj ファイルへのパス（多面体の隣接関係データ）
//   poly     : 結果を格納する Polyhedron 構造体への参照
//
// Output:
//   Returns true on success, false on failure (file not found or parse error).
//   Fills poly.num_faces, poly.gon_list, poly.adj_edges, and poly.adj_faces.
//
// 出力:
//   成功時は true、失敗時は false を返す（ファイルが見つからない、またはパースエラー）。
//   poly.num_faces, poly.gon_list, poly.adj_edges, poly.adj_faces を設定する。
//
// Guarantee:
//   - On success, poly is fully populated with valid adjacency data
//   - On failure, error message is written to std::cerr
//   - poly may be partially modified on failure; caller should check return value
//
// 保証:
//   - 成功時、poly は有効な隣接関係データで完全に設定される
//   - 失敗時、エラーメッセージが std::cerr に書き込まれる
//   - 失敗時、poly は部分的に変更されている可能性がある。呼び出し側は戻り値を確認すること
//
// File format (.adj):
//   NF<number_of_faces>
//   For each face:
//     N<gon>
//     E<edge_id_1> <edge_id_2> ...
//     F<face_id_1> <face_id_2> ...
//
// ファイル形式 (.adj):
//   NF<面の数>
//   各面について:
//     N<辺数>
//     E<辺ID_1> <辺ID_2> ...
//     F<面ID_1> <面ID_2> ...
//
// ----------------------------------------------------------------------------
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

        // Move to the next face after reading all N, E, and F elements.
        // N, E, F の要素を読み込んだら次の面へ移動。
        if (hasN && hasE && hasF) {
            current_face++;
            hasN = hasE = hasF = false;
        }
    }

    return true;
}

// ----------------------------------------------------------------------------
// loadBasePairsFromFile
// ----------------------------------------------------------------------------
//
// Input:
//   base_path  : Path to the .base file (base face-edge pairs)
//   base_pairs : Reference to a vector to be filled with (face, edge) pairs
//
// 入力:
//   base_path  : .base ファイルへのパス（基準面・辺のペア）
//   base_pairs : (面, 辺) ペアで埋められるベクターへの参照
//
// Output:
//   Returns true on success, false on failure (file not found or parse error).
//   Fills base_pairs with pairs of (base_face, base_edge).
//
// 出力:
//   成功時は true、失敗時は false を返す（ファイルが見つからない、またはパースエラー）。
//   base_pairs を (基準面, 基準辺) のペアで設定する。
//
// Guarantee:
//   - On success, base_pairs contains at least one valid pair
//   - On failure, error message is written to std::cerr
//   - base_pairs may be partially modified on failure; caller should check return value
//
// 保証:
//   - 成功時、base_pairs は少なくとも1つの有効なペアを含む
//   - 失敗時、エラーメッセージが std::cerr に書き込まれる
//   - 失敗時、base_pairs は部分的に変更されている可能性がある。呼び出し側は戻り値を確認すること
//
// File format (.base):
//   Each line contains two integers: <face_id> <edge_id>
//
// ファイル形式 (.base):
//   各行に2つの整数: <面ID> <辺ID>
//
// ----------------------------------------------------------------------------
inline bool loadBasePairsFromFile(const std::string& base_path, std::vector<std::pair<int, int>>& base_pairs) {
    std::ifstream infile(base_path);
    if (!infile) {
        std::cerr << "Error: Cannot open .base file: " << base_path << std::endl;
        return false;
    }

    int face, edge;
    while (infile >> face >> edge) {
        base_pairs.emplace_back(face, edge);
    }

    return true;
}

// ============================================================================
// Symmetry Detection
// ============================================================================

// ----------------------------------------------------------------------------
// isSymmetricFromFilename
// ----------------------------------------------------------------------------
//
// Input:
//   adj_path : Path to the .adj file (used for filename extraction)
//
// 入力:
//   adj_path : .adj ファイルへのパス（ファイル名抽出に使用）
//
// Output:
//   Returns true if the polyhedron is considered symmetric based on filename
//   conventions; false otherwise.
//
// 出力:
//   ファイル名の規約に基づいて多面体が対称とみなされる場合 true、
//   それ以外の場合 false を返す。
//
// Guarantee:
//   - Deterministic result based on filename prefix
//   - No side effects
//
// 保証:
//   - ファイル名のプレフィックスに基づく決定的な結果
//   - 副作用なし
//
// Symmetry rules:
//   - Filename starts with 'a', 'p', or 'r': symmetric
//   - Filename starts with 's' followed by 01-11: symmetric
//   - Otherwise: not symmetric
//
// 対称性の規則:
//   - ファイル名が 'a', 'p', 'r' で始まる: 対称
//   - ファイル名が 's' に続いて 01～11: 対称
//   - それ以外: 非対称
//
// ----------------------------------------------------------------------------
inline bool isSymmetricFromFilename(const std::string& adj_path) {
    // Extract the filename from the path.
    // パスからファイル名を抽出する。
    std::string filename = adj_path.substr(adj_path.find_last_of("/\\") + 1);
    if (filename.empty()) return false;

    char prefix = filename[0];
    if (prefix == 'a' || prefix == 'p' || prefix == 'r') return true;

    if (filename.size() >= 3 && prefix == 's') {
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

}  // namespace IOUtil

#endif  // REORG_IOUTIL_HPP
