#include <pybind11/pybind11.h>

#include "tca/core.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "Native C++ core for TCA";

    m.def("backend_name", &tca::backend_name);
}