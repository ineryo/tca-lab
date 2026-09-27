#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <array>
#include <optional>
#include <vector>

#include "tca/geometry/algorithms.hpp"
#include "tca/geometry/primitives.hpp"

namespace py = pybind11;

namespace {

using PointArray = py::array_t<double, py::array::c_style>;

tca::geometry::Point2 parse_point(const PointArray& value) {

    if (value.ndim() != 1 || value.shape(0) != 2) {
        throw py::value_error("point must have shape (2,)");
    }

    auto view = value.unchecked<1>();

    return {
        view(0),
        view(1),
    };
}

std::vector<tca::geometry::Point2> parse_points(const PointArray& value) {

    if (value.ndim() != 2 || value.shape(1) != 2) {
        throw py::value_error("points must have shape (n, 2)");
    }

    auto view = value.unchecked<2>();

    std::vector<tca::geometry::Point2> points;
    points.reserve(value.shape(0));

    for (py::ssize_t i = 0; i < value.shape(0); ++i) {
        points.push_back({
            view(i, 0),
            view(i, 1),
        });
    }

    return points;
}

tca::geometry::Triangle2 parse_triangle(const PointArray& value) {

    if (value.ndim() != 2 || value.shape(0) != 3 || value.shape(1) != 2) {
        throw py::value_error("triangle must have shape (3, 2)");
    }

    auto view = value.unchecked<2>();

    return {{
        {view(0, 0), view(0, 1)},
        {view(1, 0), view(1, 1)},
        {view(2, 0), view(2, 1)},
    }};
}

} // namespace

void bind_geometry(py::module_& m) {

    m.def(
        "pseudo_angle",
        [](const PointArray& vector) {
            return tca::geometry::pseudo_angle(parse_point(vector));
        },
        py::arg("vector"));

    m.def(
        "entre",
        [](const PointArray& u, const PointArray& v, const PointArray& w) {
            return tca::geometry::entre(parse_point(u), parse_point(v), parse_point(w));
        },
        py::arg("u"), py::arg("v"), py::arg("w"));

    m.def(
        "oriented_area",
        [](const PointArray& vertices) {
            const auto points = parse_points(vertices);
            return tca::geometry::oriented_area(points);
        },
        py::arg("vertices"));

    m.def(
        "barycentric_coordinates",
        [](const PointArray& point, const PointArray& triangle) {
            return tca::geometry::barycentric_coordinates(parse_point(point),
                                                          parse_triangle(triangle));
        },
        py::arg("point"), py::arg("triangle"));

    m.def(
        "locate_point_in_triangle",
        [](const PointArray& point, const PointArray& triangle) {
            return tca::geometry::locate_point_in_triangle(parse_point(point),
                                                           parse_triangle(triangle));
        },
        py::arg("point"), py::arg("triangle"));

    m.def(
        "triangles_are_disjoint",
        [](const PointArray& first, const PointArray& second) {
            return tca::geometry::triangles_are_disjoint(parse_triangle(first),
                                                         parse_triangle(second));
        },
        py::arg("first"), py::arg("second"));

    m.def(
        "is_convex",
        [](const PointArray& polygon) {
            return tca::geometry::is_convex(parse_points(polygon));
        },
        py::arg("polygon"));

    py::class_<tca::geometry::RayIntersection>(m, "RayIntersection")
        .def_property_readonly("point",
                               [](const tca::geometry::RayIntersection& intersection) {
                                   return std::array<double, 2>{
                                       intersection.point.x,
                                       intersection.point.y,
                                   };
                               })
        .def_readonly("edge_index", &tca::geometry::RayIntersection::edge_index);

    m.def(
        "first_horizontal_intersection",
        [](const PointArray& point, const PointArray& polygon) {
            return tca::geometry::first_horizontal_intersection(parse_point(point),
                                                                parse_points(polygon));
        },
        py::arg("point"), py::arg("polygon"));

    m.def(
        "locate_from_first_intersection",
        [](const PointArray& point, const PointArray& polygon,
           const std::optional<tca::geometry::RayIntersection>& intersection) {
            return tca::geometry::locate_from_first_intersection(
                parse_point(point), parse_points(polygon), intersection);
        },
        py::arg("point"), py::arg("polygon"), py::arg("intersection"));
}