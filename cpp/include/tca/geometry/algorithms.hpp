#pragma once

#include <optional>

#include "tca/geometry/types.hpp"

namespace tca::geometry {

bool triangles_are_disjoint(const Triangle2& first, const Triangle2& second);

bool is_convex(const Polygon2& polygon);

std::optional<RayIntersection> first_horizontal_intersection(const Point2& point,
                                                             const Polygon2& polygon);

int locate_from_first_intersection(const Point2& point, const Polygon2& polygon,
                                   const std::optional<RayIntersection>& intersection);

} // namespace tca::geometry