#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <span>
#include <stdexcept>

#include "tca/algorithms/sorting/selection_sort.hpp"
#include "tca/core/instrumentation/metrics.hpp"

namespace py = pybind11;

void bind_sorting(py::module_& m) {
    m.def(
        "selection_sort",
        [](py::array_t<double, py::array::c_style> values, py::object metrics) {
            if (values.ndim() != 1) {
                throw std::runtime_error(
                    "selection_sort expects a one-dimensional array");
            }

            std::span<double> view(values.mutable_data(),
                                   static_cast<std::size_t>(values.size()));

            if (metrics.is_none()) {
                tca::algorithms::selection_sort(view);
                return;
            }

            tca::instrumentation::Metrics native_metrics;

            tca::algorithms::selection_sort(view, native_metrics);

            metrics.attr("comparisons") =
                metrics.attr("comparisons").cast<std::size_t>() +
                native_metrics.comparisons;

            metrics.attr("swaps") =
                metrics.attr("swaps").cast<std::size_t>() + native_metrics.swaps;
        },
        py::arg("values"), py::arg("metrics") = py::none());
}