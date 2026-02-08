// ============================================================================
// JsonUtil.hpp
// ============================================================================
//
// What this file does:
//   Provides utility functions for outputting partial unfoldings in JSON Lines
//   (JSONL) format, including numeric rounding to ensure consistent precision.
//
// このファイルの役割:
//   部分展開図を JSON Lines (JSONL) 形式で出力するユーティリティ関数を提供する。
//   一貫した精度を保証するための数値丸め処理を含む。
//
// Responsibility in the project:
//   - Rounds numeric values (x, y, angle_deg) to 6 decimal places
//   - Serializes partial unfoldings as JSONL records (1 line per unfolding)
//   - Normalizes angles before output
//   - Does NOT handle file I/O or search logic
//
// プロジェクト内での責務:
//   - 数値 (x, y, angle_deg) を小数点以下6桁に丸める
//   - 部分展開図をJSONLレコードとしてシリアライズ（1行=1展開図）
//   - 出力前に角度を正規化
//   - ファイルI/Oや探索ロジックは担当しない
//
// Phase 1 における位置づけ:
//   Output layer for Phase 1. Converts internal data structures to JSONL format.
//   Ensures consistent numeric precision for legacy comparison and reproducibility.
//   Phase 1の出力層として機能する。内部データ構造をJSONL形式に変換する。
//   legacy比較と再現性のために一貫した数値精度を保証する。
//
// ============================================================================

#ifndef REORG_JSON_UTIL_HPP
#define REORG_JSON_UTIL_HPP

#include "UnfoldedFace.hpp"
#include "GeometryUtil.hpp"
#include <vector>
#include <ostream>
#include <iomanip>
#include <cmath>

namespace JsonUtil {

// ============================================================================
// Numeric Rounding
// ============================================================================

// ----------------------------------------------------------------------------
// roundTo6Decimals
// ----------------------------------------------------------------------------
//
// Input:
//   value : A floating-point number
//
// 入力:
//   value : 浮動小数点数
//
// Output:
//   The input value rounded to 6 decimal places using "half away from zero"
//   rounding mode.
//
// 出力:
//   "half away from zero" 丸めモードを使用して、小数点以下6桁に丸められた
//   入力値。
//
// Guarantee:
//   - Returns a value with at most 6 decimal digits of precision
//   - Uses symmetric rounding: 0.5 rounds away from zero
//   - No side effects
//
// 保証:
//   - 小数点以下最大6桁の精度を持つ値を返す
//   - 対称丸め: 0.5 は0から遠ざかる方向に丸められる
//   - 副作用なし
//
// Rationale:
//   This rounding is applied to ensure consistent output for legacy comparison
//   and reproducibility in Phase 1. The 6-digit precision is sufficient for
//   geometric calculations while keeping output size reasonable.
//
// 根拠:
//   この丸めは、Phase 1でのlegacy比較と再現性を保証するために適用される。
//   6桁の精度は幾何計算に十分であり、出力サイズも適度に保たれる。
//
// ----------------------------------------------------------------------------
inline double roundTo6Decimals(double value) {
    // Scale by 1e6, round, and scale back
    // 1e6 倍して round し、1e6 で割る
    double scaled = value * 1000000.0;
    double rounded = (scaled >= 0.0) ? std::floor(scaled + 0.5) : std::ceil(scaled - 0.5);
    return rounded / 1000000.0;
}

// ============================================================================
// JSONL Output
// ============================================================================

// ----------------------------------------------------------------------------
// writeJsonlRecord
// ----------------------------------------------------------------------------
//
// Input:
//   out                : Output stream to write the JSONL record
//   base_face          : ID of the base face
//   base_edge          : ID of the base edge
//   symmetric_used     : Whether symmetry pruning was enabled for this unfolding
//   partial_unfolding  : Vector of UnfoldedFace representing the partial unfolding path
//
// 入力:
//   out                : JSONLレコードを書き込む出力ストリーム
//   base_face          : 基準面のID
//   base_edge          : 基準辺のID
//   symmetric_used     : この展開図で対称性枝刈りが有効だったか
//   partial_unfolding  : 部分展開図のパスを表す UnfoldedFace のベクター
//
// Output:
//   Writes a single JSONL record (one line) to the output stream.
//   The record includes schema_version, record_type, base_pair, symmetric_used,
//   and the array of faces with rounded coordinates.
//
// 出力:
//   出力ストリームに1つのJSONLレコード（1行）を書き込む。
//   レコードには schema_version, record_type, base_pair, symmetric_used、
//   および丸められた座標を持つ faces 配列が含まれる。
//
// Guarantee:
//   - Outputs a single line terminated by '\n'
//   - All numeric values (x, y, angle_deg) are rounded to 6 decimal places
//   - Angles are normalized to [-180, 180] before rounding
//   - Valid JSON format (parseable by standard JSON parsers)
//   - Modifies the output stream
//
// 保証:
//   - '\n' で終わる1行を出力
//   - すべての数値 (x, y, angle_deg) は小数点以下6桁に丸められる
//   - 角度は丸める前に [-180, 180] に正規化される
//   - 有効なJSON形式（標準のJSONパーサで解析可能）
//   - 出力ストリームを変更する
//
// JSONL schema (Phase 1):
//   {
//     "schema_version": 1,
//     "record_type": "partial_unfolding",
//     "base_pair": {"base_face": <int>, "base_edge": <int>},
//     "symmetric_used": <bool>,
//     "faces": [
//       {"face_id": <int>, "gon": <int>, "edge_id": <int>,
//        "x": <float>, "y": <float>, "angle_deg": <float>},
//       ...
//     ]
//   }
//
// ----------------------------------------------------------------------------
inline void writeJsonlRecord(
    std::ostream& out,
    int base_face,
    int base_edge,
    bool symmetric_used,
    const std::vector<UnfoldedFace>& partial_unfolding)
{
    out << "{";

    // schema_version: Version 1 for Phase 1 output
    // schema_version: Phase 1 出力のバージョン1
    out << "\"schema_version\":1,";

    // record_type: Identifies this as a partial unfolding record
    // record_type: 部分展開図レコードであることを識別
    out << "\"record_type\":\"partial_unfolding\",";

    // base_pair: The (face, edge) pair used to initialize this unfolding
    // base_pair: この展開図を初期化するために使用された (面, 辺) ペア
    out << "\"base_pair\":{\"base_face\":" << base_face
        << ",\"base_edge\":" << base_edge << "},";

    // symmetric_used: Whether symmetry pruning was enabled
    // symmetric_used: 対称性枝刈りが有効だったか
    out << "\"symmetric_used\":" << (symmetric_used ? "true" : "false") << ",";

    // faces: Array of faces in the partial unfolding path
    // faces: 部分展開図パス内の面の配列
    out << "\"faces\":[";
    for (size_t i = 0; i < partial_unfolding.size(); ++i) {
        const auto& f = partial_unfolding[i];

        // Normalize angle to [-180, 180] before rounding
        // 丸める前に角度を [-180, 180] に正規化
        double normalized_angle = f.angle;
        GeometryUtil::normalizeAngle(normalized_angle);

        // Round coordinates and angle to 6 decimal places
        // 座標と角度を小数点以下6桁に丸める
        double x_rounded = roundTo6Decimals(f.x);
        double y_rounded = roundTo6Decimals(f.y);
        double angle_rounded = roundTo6Decimals(normalized_angle);

        out << "{\"face_id\":" << f.face_id
            << ",\"gon\":" << f.gon
            << ",\"edge_id\":" << f.edge_id
            << ",\"x\":" << std::fixed << std::setprecision(6) << x_rounded
            << ",\"y\":" << std::fixed << std::setprecision(6) << y_rounded
            << ",\"angle_deg\":" << std::fixed << std::setprecision(6) << angle_rounded
            << "}";

        if (i < partial_unfolding.size() - 1) {
            out << ",";
        }
    }
    out << "]";

    out << "}\n";
}

}  // namespace JsonUtil

#endif  // REORG_JSON_UTIL_HPP
