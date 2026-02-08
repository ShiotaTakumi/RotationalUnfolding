// ============================================================================
// IOUtil.hpp
// ============================================================================
//
// What this file does:
//   Provides utility functions for loading polyhedron data from JSON input files
//   (polyhedron.json and root_pairs.json formats).
//
// このファイルの役割:
//   JSON入力ファイル（polyhedron.json および root_pairs.json 形式）から
//   多面体データを読み込むユーティリティ関数を提供する。
//
// Responsibility in the project:
//   - Parses polyhedron.json to construct Polyhedron structures
//   - Parses root_pairs.json to load base face-edge pairs
//   - Validates JSON schema versions
//   - Does NOT handle output or unfolding logic
//
// プロジェクト内での責務:
//   - polyhedron.json をパースして Polyhedron 構造を構築
//   - root_pairs.json をパースして基準面・辺のペアを読み込み
//   - JSON スキーマバージョンを検証
//   - 出力や展開ロジックは担当しない
//
// Phase 1 における位置づけ:
//   Input layer for loading polyhedron data in the new JSON format.
//   Replaces the legacy .adj/.base input format.
//   Phase 1では、新しいJSON形式で多面体データを読み込む入力層として機能する。
//   legacy の .adj/.base 入力形式を置き換える。
//
// ============================================================================

#ifndef REORG_IOUTIL_HPP
#define REORG_IOUTIL_HPP

#include "Polyhedron.hpp"
#include "json.hpp"
#include <string>
#include <fstream>
#include <iostream>
#include <vector>

namespace IOUtil {

using json = nlohmann::json;

// ============================================================================
// JSON Input File Parsers
// ============================================================================

// ----------------------------------------------------------------------------
// loadPolyhedronFromJson
// ----------------------------------------------------------------------------
//
// Input:
//   json_path : Path to the polyhedron.json file
//   poly      : Reference to a Polyhedron structure to be filled
//
// 入力:
//   json_path : polyhedron.json ファイルへのパス
//   poly      : 結果を格納する Polyhedron 構造体への参照
//
// Output:
//   Returns true on success, false on failure (file not found, parse error,
//   or schema validation error).
//   Fills poly.num_faces, poly.gon_list, poly.adj_edges, and poly.adj_faces.
//
// 出力:
//   成功時は true、失敗時は false を返す（ファイルが見つからない、パースエラー、
//   またはスキーマ検証エラー）。
//   poly.num_faces, poly.gon_list, poly.adj_edges, poly.adj_faces を設定する。
//
// Guarantee:
//   - On success, poly is fully populated with valid adjacency data
//   - On failure, error message is written to std::cerr
//   - poly may be partially modified on failure; caller should check return value
//   - Validates schema_version is 1
//
// 保証:
//   - 成功時、poly は有効な隣接関係データで完全に設定される
//   - 失敗時、エラーメッセージが std::cerr に書き込まれる
//   - 失敗時、poly は部分的に変更されている可能性がある。呼び出し側は戻り値を確認すること
//   - schema_version が 1 であることを検証
//
// JSON schema (polyhedron.json):
//   {
//     "schema_version": 1,
//     "polyhedron": {
//       "class": string,
//       "name": string
//     },
//     "faces": [
//       {
//         "face_id": int,
//         "gon": int,
//         "neighbors": [
//           {"edge_id": int, "face_id": int},
//           ...
//         ]
//       },
//       ...
//     ]
//   }
//
// ----------------------------------------------------------------------------
inline bool loadPolyhedronFromJson(const std::string& json_path, Polyhedron& poly) {
    std::ifstream file(json_path);
    if (!file) {
        std::cerr << "Error: Cannot open polyhedron.json file: " << json_path << std::endl;
        return false;
    }

    json j;
    try {
        file >> j;
    } catch (const json::parse_error& e) {
        std::cerr << "Error: JSON parse error in " << json_path << ": " << e.what() << std::endl;
        return false;
    }

    // Validate schema version
    // スキーマバージョンを検証
    if (!j.contains("schema_version") || j["schema_version"] != 1) {
        std::cerr << "Error: Unsupported or missing schema_version in " << json_path << std::endl;
        return false;
    }

    // Validate required fields
    // 必須フィールドを検証
    if (!j.contains("faces") || !j["faces"].is_array()) {
        std::cerr << "Error: Missing or invalid 'faces' field in " << json_path << std::endl;
        return false;
    }

    const auto& faces_array = j["faces"];
    poly.num_faces = faces_array.size();
    poly.gon_list.resize(poly.num_faces);
    poly.adj_edges.resize(poly.num_faces);
    poly.adj_faces.resize(poly.num_faces);

    // Parse each face
    // 各面を解析
    for (const auto& face_obj : faces_array) {
        if (!face_obj.contains("face_id") || !face_obj.contains("gon") || !face_obj.contains("neighbors")) {
            std::cerr << "Error: Face object missing required fields in " << json_path << std::endl;
            return false;
        }

        int face_id = face_obj["face_id"];
        int gon = face_obj["gon"];

        if (face_id < 0 || face_id >= poly.num_faces) {
            std::cerr << "Error: Invalid face_id " << face_id << " in " << json_path << std::endl;
            return false;
        }

        poly.gon_list[face_id] = gon;

        const auto& neighbors = face_obj["neighbors"];
        if (!neighbors.is_array()) {
            std::cerr << "Error: 'neighbors' must be an array in " << json_path << std::endl;
            return false;
        }

        for (const auto& neighbor : neighbors) {
            if (!neighbor.contains("edge_id") || !neighbor.contains("face_id")) {
                std::cerr << "Error: Neighbor object missing required fields in " << json_path << std::endl;
                return false;
            }

            int edge_id = neighbor["edge_id"];
            int neighbor_face_id = neighbor["face_id"];

            poly.adj_edges[face_id].push_back(edge_id);
            poly.adj_faces[face_id].push_back(neighbor_face_id);
        }
    }

    return true;
}

// ----------------------------------------------------------------------------
// loadRootPairsFromJson
// ----------------------------------------------------------------------------
//
// Input:
//   json_path  : Path to the root_pairs.json file
//   root_pairs : Reference to a vector to be filled with (face, edge) pairs
//
// 入力:
//   json_path  : root_pairs.json ファイルへのパス
//   root_pairs : (面, 辺) ペアで埋められるベクターへの参照
//
// Output:
//   Returns true on success, false on failure (file not found, parse error,
//   or schema validation error).
//   Fills root_pairs with pairs of (base_face, base_edge).
//
// 出力:
//   成功時は true、失敗時は false を返す（ファイルが見つからない、パースエラー、
//   またはスキーマ検証エラー）。
//   root_pairs を (基準面, 基準辺) のペアで設定する。
//
// Guarantee:
//   - On success, root_pairs contains at least one valid pair
//   - On failure, error message is written to std::cerr
//   - root_pairs may be partially modified on failure; caller should check return value
//   - Validates schema_version is 1
//
// 保証:
//   - 成功時、root_pairs は少なくとも1つの有効なペアを含む
//   - 失敗時、エラーメッセージが std::cerr に書き込まれる
//   - 失敗時、root_pairs は部分的に変更されている可能性がある。呼び出し側は戻り値を確認すること
//   - schema_version が 1 であることを検証
//
// JSON schema (root_pairs.json):
//   {
//     "schema_version": 1,
//     "root_pairs": [
//       {"base_face": int, "base_edge": int},
//       ...
//     ]
//   }
//
// ----------------------------------------------------------------------------
inline bool loadRootPairsFromJson(const std::string& json_path, std::vector<std::pair<int, int>>& root_pairs) {
    std::ifstream file(json_path);
    if (!file) {
        std::cerr << "Error: Cannot open root_pairs.json file: " << json_path << std::endl;
        return false;
    }

    json j;
    try {
        file >> j;
    } catch (const json::parse_error& e) {
        std::cerr << "Error: JSON parse error in " << json_path << ": " << e.what() << std::endl;
        return false;
    }

    // Validate schema version
    // スキーマバージョンを検証
    if (!j.contains("schema_version") || j["schema_version"] != 1) {
        std::cerr << "Error: Unsupported or missing schema_version in " << json_path << std::endl;
        return false;
    }

    // Validate required fields
    // 必須フィールドを検証
    if (!j.contains("root_pairs") || !j["root_pairs"].is_array()) {
        std::cerr << "Error: Missing or invalid 'root_pairs' field in " << json_path << std::endl;
        return false;
    }

    const auto& pairs_array = j["root_pairs"];
    for (const auto& pair_obj : pairs_array) {
        if (!pair_obj.contains("base_face") || !pair_obj.contains("base_edge")) {
            std::cerr << "Error: Root pair object missing required fields in " << json_path << std::endl;
            return false;
        }

        int base_face = pair_obj["base_face"];
        int base_edge = pair_obj["base_edge"];
        root_pairs.emplace_back(base_face, base_edge);
    }

    if (root_pairs.empty()) {
        std::cerr << "Error: No root pairs found in " << json_path << std::endl;
        return false;
    }

    return true;
}

// ============================================================================
// Symmetry Detection (unchanged from legacy)
// ============================================================================

// ----------------------------------------------------------------------------
// isSymmetricFromPolyName
// ----------------------------------------------------------------------------
//
// Input:
//   poly_name : Name of the polyhedron (e.g., "s05", "p10", "a15")
//
// 入力:
//   poly_name : 多面体の名前（例: "s05", "p10", "a15"）
//
// Output:
//   Returns true if the polyhedron is considered symmetric based on naming
//   conventions; false otherwise.
//
// 出力:
//   命名規約に基づいて多面体が対称とみなされる場合 true、
//   それ以外の場合 false を返す。
//
// Guarantee:
//   - Deterministic result based on polyhedron name prefix
//   - No side effects
//
// 保証:
//   - 多面体名のプレフィックスに基づく決定的な結果
//   - 副作用なし
//
// Symmetry rules (same as legacy):
//   - Name starts with 'a', 'p', or 'r': symmetric
//   - Name starts with 's' followed by 01-11: symmetric
//   - Otherwise: not symmetric
//
// 対称性の規則（legacy と同じ）:
//   - 名前が 'a', 'p', 'r' で始まる: 対称
//   - 名前が 's' に続いて 01～11: 対称
//   - それ以外: 非対称
//
// ----------------------------------------------------------------------------
inline bool isSymmetricFromPolyName(const std::string& poly_name) {
    if (poly_name.empty()) return false;

    char prefix = poly_name[0];
    if (prefix == 'a' || prefix == 'p' || prefix == 'r') return true;

    if (poly_name.size() >= 3 && prefix == 's') {
        std::string num_part = poly_name.substr(1, 2);
        try {
            int num = std::stoi(num_part);
            return (1 <= num && num <= 11);
        } catch (...) {
            return false;
        }
    }
    return false;
}

// ----------------------------------------------------------------------------
// extractPolyNameFromJson
// ----------------------------------------------------------------------------
//
// Input:
//   json_path : Path to the polyhedron.json file
//
// 入力:
//   json_path : polyhedron.json ファイルへのパス
//
// Output:
//   Returns the polyhedron name if found in the JSON; empty string on failure.
//
// 出力:
//   JSON 内に見つかった場合は多面体名を返す。失敗時は空文字列。
//
// Guarantee:
//   - Does not modify any external state
//   - Returns empty string if polyhedron.name field is missing
//
// 保証:
//   - 外部状態を変更しない
//   - polyhedron.name フィールドが欠落している場合は空文字列を返す
//
// ----------------------------------------------------------------------------
inline std::string extractPolyNameFromJson(const std::string& json_path) {
    std::ifstream file(json_path);
    if (!file) {
        return "";
    }

    json j;
    try {
        file >> j;
        if (j.contains("polyhedron") && j["polyhedron"].contains("name")) {
            return j["polyhedron"]["name"];
        }
    } catch (...) {
        return "";
    }

    return "";
}

}  // namespace IOUtil

#endif  // REORG_IOUTIL_HPP
