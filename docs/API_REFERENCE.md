# TCA API and implementation reference {#mainpage}

TCA Lab is a standalone C++/Python project for algorithms, computational
geometry, instrumentation, experiments, and interactive visualization. This
reference describes the reusable implementation surface. Assignment statements,
notebooks, rendered artifacts, reports, and presentations retain their own
canonical workflows and are deliberately outside this API build.

## Build this reference

The only required documentation tool is Doxygen. From a TCA checkout:

```bash
mkdir -p build/doxygen
doxygen Doxyfile
```

Open `build/doxygen/html/index.html` in a browser. The generated output is
intentionally untracked. Doxygen 1.9.8 was used to validate this configuration.

Plain Doxygen is sufficient for the current C++ headers, Python-facing source
contracts, module navigation, and cross-references, so no second documentation
stack is introduced. Graphviz is deliberately not required: the current API
surface remains navigable through Doxygen's normal tree and source links.

## API map

- **C++ core:** `cpp/include/tca/` exposes the reusable native library in the
  `tca` namespace: sorting, instrumentation, deterministic pseudo-randomness,
  quantization, and the two-dimensional geometry kernel.
- **Python library:** `src/tca/` supplies the public sorting facade, Python
  reference implementations, trace/replay support, analysis, experiment, and
  Plotly visualization helpers.
- **C++/Python boundary:** `cpp/bindings/` builds `tca._core` with pybind11.
  Python clients should normally use `tca.algorithms.sorting`; geometry is
  currently exposed through `tca.geometry`.

## Boundary contract

The native sorting bindings operate **in place** on a one-dimensional,
C-contiguous `numpy.float64` array. The Python facade validates those
requirements before selecting the `cpp` backend. The `python` backend is the
only backend that supports a full `Trace`; both backends can accumulate the
shared `Metrics` counters.

Geometry bindings accept C-contiguous `numpy.float64` inputs shaped `(2,)` for
a point, `(3, 2)` for a triangle, and `(n, 2)` for a point sequence. The kernel
is practical floating-point geometry, not an exact-predicate library; its
central tolerance policy is documented in `tca::geometry::DEFAULT_TOLERANCE`.

## Scope and related material

This reference does not replace existing course material:

- Pandoc remains responsible for existing reports and documents.
- Marp and the Marp Artifact Updater remain responsible for presentations and
  their synchronized regions.
- Notebooks and nbconvert remain responsible for notebook execution/publication.
- Plotly remains responsible for existing interactive artifacts.

For course-facing entry points and the preserved deliverables, see the repository
root README, the assignment READMEs, and `docs/geometry_conventions.md`.
