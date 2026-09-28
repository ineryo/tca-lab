#pragma once

#include <array>
#include <span>

#include "tca/geometry/types.hpp"

namespace tca::geometry {

/** Returns the octant-based pseudo-angle of a nonzero vector. */
double pseudo_angle(const Point2& vector);

/** Returns the two-dimensional scalar cross product of @p first and @p second. */
double cross(const Vector2& first, const Vector2& second);

/** Classifies @p w relative to the convex angle from @p u to @p v (0, 1, or 2). */
int entre(const Point2& u, const Point2& v, const Point2& w);

/** Returns the signed area of a polygon with at least three vertices. */
double oriented_area(std::span<const Point2> vertices);

/** Returns barycentric coordinates of @p point in a nondegenerate triangle. */
std::array<double, 3> barycentric_coordinates(const Point2& point,
                                              const Triangle2& triangle);

/** Returns 0 (outside), 1 (inside), or 2 (boundary) for a nondegenerate triangle. */
int locate_point_in_triangle(const Point2& point, const Triangle2& triangle);

/** Returns whether two closed segments intersect, including endpoint contact. */
bool segments_intersect(const Segment2& first, const Segment2& second);

} // namespace tca::geometry