#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <cstddef>
#include <cstdint>
#include <span>
#include <stdexcept>
#include <string>

#include "tca/algorithms/sorting/quick_sort.hpp"
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

void accumulate_metrics(py::object& metrics,
                        const tca::instrumentation::Metrics& native_metrics) {
    native_metrics.for_each_metric([&metrics](const char* name, std::size_t value) {
        const auto previous = metrics.attr(name).cast<std::size_t>();

        metrics.attr(name) = py::int_(previous + value);
    });
}

tca::algorithms::QuickPivot parse_quick_pivot(const std::string& pivot) {
    if (pivot == "first") {
        return tca::algorithms::QuickPivot::First;
    }

    if (pivot == "quarter") {
        return tca::algorithms::QuickPivot::Quarter;
    }

    if (pivot == "random") {
        return tca::algorithms::QuickPivot::Random;
    }

    throw std::invalid_argument("unknown pivot strategy: " + pivot);
}

tca::algorithms::QuickRecursion parse_quick_recursion(const std::string& recursion) {
    if (recursion == "classic") {
        return tca::algorithms::QuickRecursion::Classic;
    }

    if (recursion == "bounded") {
        return tca::algorithms::QuickRecursion::Bounded;
    }

    throw std::invalid_argument("unknown recursion strategy: " + recursion);
}

void quick_sort_array(Array values, const std::string& pivot,
                      const std::string& recursion, std::uint64_t seed,
                      py::object metrics) {
    auto view = array_view(values);

    const tca::algorithms::QuickSortOptions options{
        parse_quick_pivot(pivot),
        parse_quick_recursion(recursion),
        seed,
    };

    if (metrics.is_none()) {
        tca::algorithms::quick_sort(view, options);

        return;
    }

    tca::instrumentation::Metrics native_metrics;

    tca::algorithms::quick_sort(view, native_metrics, options);

    accumulate_metrics(metrics, native_metrics);
}

void sort_array(Array values, const std::string& method, py::object metrics) {
    auto view = array_view(values);

    if (metrics.is_none()) {
        tca::algorithms::sort(view, method);

        return;
    }

    tca::instrumentation::Metrics native_metrics;

    tca::algorithms::sort(view, method, native_metrics);

    accumulate_metrics(metrics, native_metrics);
}

} // namespace

void bind_sorting(py::module_& m) {
    m.def("sort", &sort_array, py::arg("values"), py::arg("method"),
          py::arg("metrics") = py::none());

    m.def("quick_sort", &quick_sort_array, py::arg("values"),
          py::arg("pivot") = "first", py::arg("recursion") = "bounded",
          py::arg("seed") = 0, py::arg("metrics") = py::none());

    m.def("available_sorting_algorithms", []() {
        py::list result;

        for (const auto method : tca::algorithms::available_sorting_algorithms()) {
            result.append(py::str(std::string(method)));
        }

        return result;
    });

    m.def("available_metrics", []() {
        py::list result;

        const tca::instrumentation::Metrics metrics;

        metrics.for_each_metric(
            [&result](const char* name, std::size_t) { result.append(py::str(name)); });

        return result;
    });
}