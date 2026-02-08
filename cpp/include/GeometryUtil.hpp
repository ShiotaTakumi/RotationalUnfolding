// ============================================================================
// GeometryUtil.hpp
// ============================================================================
//
// What this file does:
//   Provides geometry utility functions for regular polygons (n-gons).
//   All calculations assume unit edge length.
//
// このファイルの役割:
//   正多角形（n角形）の幾何計算ユーティリティ関数を提供する。
//   すべての計算は辺長1を前提とする。
//
// Responsibility in the project:
//   - Computes circumradius and inradius for regular n-gons
//   - Normalizes angles to [-180, 180] degrees
//   - Computes Euclidean distance from the origin
//   - Provides a numerical buffer for floating-point error tolerance
//
// プロジェクト内での責務:
//   - 正n角形の外接円半径と内接円半径を計算
//   - 角度を [-180, 180] 度に正規化
//   - 原点からのユークリッド距離を計算
//   - 浮動小数点誤差許容のための数値バッファを提供
//
// Phase 1 における位置づけ:
//   Core utility for geometric calculations during unfolding search.
//   Used for distance-based pruning and coordinate transformations.
//   Phase 1では、展開探索中の幾何計算の中核ユーティリティ。
//   距離ベースの枝刈りと座標変換に使用される。
//
// ============================================================================

#ifndef REORG_GEOMETRY_UTIL_HPP
#define REORG_GEOMETRY_UTIL_HPP

#include <cmath>

namespace GeometryUtil {

// ============================================================================
// Constants
// ============================================================================

// ----------------------------------------------------------------------------
// Value of π (pi) fixed to 15 decimal places.
// πの値（小数点以下15桁）。
// ----------------------------------------------------------------------------
constexpr double PI = 3.141592653589793;

// ----------------------------------------------------------------------------
// Numerical buffer to avoid false checks caused by floating-point errors.
// Used for distance comparisons in overlap detection and pruning.
//
// 浮動小数点誤差による誤判定を防ぐための数値バッファ。
// 重なり判定と枝刈りにおける距離比較に使用される。
// ----------------------------------------------------------------------------
const double buffer = 0.01;

// ============================================================================
// Geometry Functions
// ============================================================================

// ----------------------------------------------------------------------------
// circumradius
// ----------------------------------------------------------------------------
//
// Input:
//   gon : Number of edges of the regular polygon (n)
//
// 入力:
//   gon : 正多角形の辺の数 (n)
//
// Output:
//   Circumradius (radius of the circumscribed circle) of the regular n-gon
//   with unit edge length.
//
// 出力:
//   辺長1の正n角形の外接円の半径。
//
// Guarantee:
//   - Returns a positive value for gon >= 3
//   - No side effects
//
// 保証:
//   - gon >= 3 の場合、正の値を返す
//   - 副作用なし
//
// ----------------------------------------------------------------------------
inline double circumradius(int gon) {
    return 1.0 / (2.0 * std::sin(PI / static_cast<double>(gon)));
}

// ----------------------------------------------------------------------------
// inradius
// ----------------------------------------------------------------------------
//
// Input:
//   gon : Number of edges of the regular polygon (n)
//
// 入力:
//   gon : 正多角形の辺の数 (n)
//
// Output:
//   Inradius (radius of the inscribed circle) of the regular n-gon
//   with unit edge length.
//
// 出力:
//   辺長1の正n角形の内接円の半径。
//
// Guarantee:
//   - Returns a positive value for gon >= 3
//   - No side effects
//
// 保証:
//   - gon >= 3 の場合、正の値を返す
//   - 副作用なし
//
// ----------------------------------------------------------------------------
inline double inradius(int gon) {
    return 1.0 / (2.0 * std::tan(PI / static_cast<double>(gon)));
}

// ----------------------------------------------------------------------------
// normalizeAngle
// ----------------------------------------------------------------------------
//
// Input:
//   degree : Angle in degrees (modified in-place)
//
// 入力:
//   degree : 度数法の角度（その場で変更される）
//
// Output:
//   None (modifies the input parameter in-place)
//
// 出力:
//   なし（入力パラメータをその場で変更）
//
// Guarantee:
//   - After this call, degree is in the range [-180, 180]
//   - Modifies the input parameter
//
// 保証:
//   - 呼び出し後、degree は [-180, 180] の範囲に収まる
//   - 入力パラメータを変更する
//
// ----------------------------------------------------------------------------
inline void normalizeAngle(double& degree) {
    while (degree < -180.0) degree += 360.0;
    while (degree > 180.0)  degree -= 360.0;
}

// ----------------------------------------------------------------------------
// getDistanceFromOrigin
// ----------------------------------------------------------------------------
//
// Input:
//   x : X-coordinate
//   y : Y-coordinate
//
// 入力:
//   x : x座標
//   y : y座標
//
// Output:
//   Euclidean distance from the origin (0, 0) to the point (x, y).
//
// 出力:
//   原点 (0, 0) から点 (x, y) までのユークリッド距離。
//
// Guarantee:
//   - Returns a non-negative value
//   - No side effects
//
// 保証:
//   - 非負の値を返す
//   - 副作用なし
//
// ----------------------------------------------------------------------------
inline double getDistanceFromOrigin(double x, double y) {
    return std::sqrt(x * x + y * y);
}

}  // namespace GeometryUtil

#endif  // REORG_GEOMETRY_UTIL_HPP
