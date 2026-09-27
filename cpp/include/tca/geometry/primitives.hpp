#pragma once

#include <array>
#include <span>

#include "tca/geometry/types.hpp"

namespace tca::geometry {

double pseudo_angle(const Point2& vector);

double cross(const Vector2& first, const Vector2& second);

int entre(const Point2& u, const Point2& v, const Point2& w);

double oriented_area(std::span<const Point2> vertices);

std::array<double, 3> barycentric_coordinates(const Point2& point,
                                              const Triangle2& triangle);

int locate_point_in_triangle(const Point2& point, const Triangle2& triangle);

bool segments_intersect(const Segment2& first, const Segment2& second);

} // namespace tca::geometry