#include <pybind11/pybind11.h>

#include "tca/core/prng.hpp"

namespace py = pybind11;

void bind_prng(py::module_& m) {
    py::class_<tca::PRNG>(m, "PRNG")
        .def(py::init<std::uint64_t>(), py::arg("seed") = 0)
        .def("next_uint64", &tca::PRNG::next_uint64)
        .def("randbelow", &tca::PRNG::randbelow);
}