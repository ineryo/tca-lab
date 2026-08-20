#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <cstddef>
#include <span>
#include <stdexcept>
#include <string>

#include "tca/algorithms/sorting/registry.hpp"
#include "tca/core/instrumentation/metrics.hpp"

namespace py = pybind11;

namespace {

using Array = py::array_t<double, py::array::c_style>;

std::span<double> array_view(Array& values) {
    if (values.ndim() != 1) {
        throw std::runtime_error("sort expects a one-dimensional array");
    }

    return {
        values.mutable_data(),
        static_cast<std::size_t>(values.size()),
    };
}

void sort_array(Array values, const std::string& method, py::object metrics) {
    auto view = array_view(values);

    if (metrics.is_none()) {
        tca::algorithms::sort(view, method);

        return;
    }

    tca::instrumentation::Metrics native_metrics;

    tca::algorithms::sort(view, method, native_metrics);

    const auto previous_comparisons = metrics.attr("comparisons").cast<std::size_t>();

    const auto previous_swaps = metrics.attr("swaps").cast<std::size_t>();

    metrics.attr("comparisons") =
        py::int_(previous_comparisons + native_metrics.comparisons);

    metrics.attr("swaps") = py::int_(previous_swaps + native_metrics.swaps);
}

} // namespace

void bind_sorting(py::module_& m) {
    m.def("sort", &sort_array, py::arg("values"), py::arg("method"),
          py::arg("metrics") = py::none());

    m.def("available_sorting_algorithms", []() {
        py::list result;

        for (const auto method : tca::algorithms::available_sorting_algorithms()) {
            result.append(py::str(std::string(method)));
        }

        return result;
    });
}