#include <pybind11/pybind11.h>

#include "tca/core/quantization.hpp"

namespace py = pybind11;

void bind_quantization(py::module_& m) {
    m.def("decimal_key", &tca::decimal_key, py::arg("value"), py::arg("digits") = 3);
}