#include <pybind11/pybind11.h>

#include "tca/core.hpp"

namespace py = pybind11;

void bind_sorting(py::module_& m);

void bind_prng(py::module_& m);

PYBIND11_MODULE(_core, m) {
    m.doc() = "Native C++ core for TCA";

    m.def("backend_name", &tca::backend_name);

    bind_prng(m);
    bind_sorting(m);
}