#ifndef GEOMETRY_UTIL_HPP
#define GEOMETRY_UTIL_HPP

#include <cmath>

namespace GeometryUtil {
    // Value of π (pi), used in trigonometric calculations.
    constexpr double PI = 3.141592653589793;

    // A small buffer added to improve numerical stability in
    // overlap detection, preventing false positives due to
    // floating-point errors.
    const double buffer = 0.01;

    // Returns the Euclidean distance from the origin to
    // the point (x, y).
    inline double getDistanceFromOrigin(double x, double y) {
        return std::sqrt(x * x + y * y);
    }

    // Normalizes the angle to the range [-180, 180] degrees.
    inline void normalizeAngle(double& degree) {
        while (degree < -180.0) degree += 360.0;
        while (degree > 180.0)  degree -= 360.0;
    }

    // Computes the circumradius of a regular polygon
    // with 'gon' sides.
    inline double circumradius(int gon) {
        return 1.0 / (2.0 * std::sin(PI / static_cast<double>(gon)));
    }

    // Computes the inradius of a regular polygon
    // with 'gon' sides.
    inline double inradius(int gon) {
        return 1.0 / (2.0 * std::tan(PI / static_cast<double>(gon)));
    }

}

#endif  // GEOMETRY_UTIL_HPP
