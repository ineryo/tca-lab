#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <span>
#include <stdexcept>

#include "tca/algorithms/sorting/selection_sort.hpp"

namespace py = pybind11;

void bind_sorting(py::module_& m) {
    m.def(
        "selection_sort",
        [](py::array_t<double, py::array::c_style> values) {
            if (values.ndim() != 1) {
                throw std::runtime_error(
                    "selection_sort expects a one-dimensional array");
            }

            std::span<double> view(values.mutable_data(),
                                   static_cast<std::size_t>(values.size()));

            tca::algorithms::selection_sort(view);
        },
        py::arg("values"));
}