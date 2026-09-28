#pragma once

#include <array> // fixed-size contiguous container
#include <cstddef>
#include <vector> // dynamic-size contiguous container

namespace tca::geometry {

/** A two-dimensional Cartesian point with double-precision coordinates. */
struct Point2 {
    double x;
    double y;
};

/** A displacement vector represented by its x and y components. */
using Vector2 = Point2;
using Segment2 = std::array<Point2, 2>;
using Triangle2 = std::array<Point2, 3>;
using Polygon2 = std::vector<Point2>;

// Armazena a primeira intersecao da semirreta horizontal com o poligono.
// `point` representa o ponto u e `edge_index` identifica o lado pi -> pi+1
// onde a intersecao ocorre. Usado na Questao 7, lista 2.
/** First intersection between the query ray and a polygon edge. */
struct RayIntersection {
    Point2 point;
    std::size_t edge_index;
};

} // namespace tca::geometry
