#pragma once

#include <optional>

#include "tca/geometry/types.hpp"

namespace tca::geometry {

/** Returns whether nondegenerate closed triangles have no common point. */
bool triangles_are_disjoint(const Triangle2& first, const Triangle2& second);

/** Returns whether a polygon has strictly consistent turn orientation. */
bool is_convex(const Polygon2& polygon);

/** Finds the nearest rightward horizontal-ray intersection, if one exists. */
std::optional<RayIntersection> first_horizontal_intersection(const Point2& point,
                                                             const Polygon2& polygon);

/**
 * Classifies a point from a first-ray intersection: 0 outside, 1 inside, 2 boundary.
 * The associated polygon edge is interpreted using the clockwise-polygon contract.
 */
int locate_from_first_intersection(const Point2& point, const Polygon2& polygon,
                                   const std::optional<RayIntersection>& intersection);

} // namespace tca::geometry