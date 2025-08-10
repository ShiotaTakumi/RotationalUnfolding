#ifndef ROTATIONAL_UNFOLDING_GEOMETRY_UTIL_HPP
#define ROTATIONAL_UNFOLDING_GEOMETRY_UTIL_HPP

#include <cmath>

namespace GeometryUtil {
    // 円周率 π の概算値（小数点以下 15 桁）を固定値として使用
    // Approximate value of π (pi) fixed to 15 decimal places.
    constexpr double PI = 3.141592653589793;

    // n 角形の外接円の半径を計算する
    // Computes the circumradius of an n-gon.
    inline double circumradius(int gon) {
        return 1.0 / (2.0 * std::sin(PI / static_cast<double>(gon)));
    }

    // 角度を [-180, 180] 度の範囲に正規化する
    // Normalizes the angle to the range [-180, 180] degrees.
    inline void normalizeAngle(double& degree) {
        while (degree < -180.0) degree += 360.0;
        while (degree > 180.0)  degree -= 360.0;
    }

    // 原点から座標 (x, y) までのユークリッド距離を計算する
    // Computes the Euclidean distance from
    // the origin to the point (x, y).
    inline double getDistanceFromOrigin(double x, double y) {
        return std::sqrt(x * x + y * y);
    }

    // 浮動小数点誤差による誤判定を防ぐためのバッファー
    // Buffer to avoid false checks caused by floating-point errors.
    const double buffer = 0.01;

    // n 角形の内接円の半径を計算する
    // Computes the inradius of an n-gon.
    inline double inradius(int gon) {
        return 1.0 / (2.0 * std::tan(PI / static_cast<double>(gon)));
    }
}

#endif  // ROTATIONAL_UNFOLDING_GEOMETRY_UTIL_HPP
