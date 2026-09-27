# TCA Lab

TCA Lab is a standalone repository for coursework and research-oriented
implementations in algorithms, computational geometry, and their presentation.
It keeps source code, experiments, notebooks, rendered artifacts, and teaching
deliverables together while preserving each assignment's own reproducible path.

## Start here

- [Sorting assignment](assignments/01-sorting/README.md) — benchmarked sorting
  implementations, interactive Plotly artifacts, and a Marp presentation.
- [Computational geometry assignment](assignments/02-geometry/README.md) —
  geometry kernel, report, and reproducible delivery notes.
- [`course/`](course/) — course-facing material and context.
- [`benchmarks/`](benchmarks/) — benchmark inputs and supporting code.

## Repository layout

```text
assignments/  completed coursework and its delivery documentation
src/          Python package source, including local visualization helpers
cpp/          C++ implementations and bindings
benchmarks/   benchmark support
course/       course material and context
tests/        repository tests
```

## Development

The repository uses Python 3.12 and `uv` for the Python environment. Consult the
assignment README before running a specific workflow: assignment deliverables,
rendering commands, and artifact ownership are intentionally local to their
subject matter.

```bash
uv sync
uv run pytest
```

## Documentation and artifacts

Markdown, notebooks, source code, and renderer inputs remain canonical in their
respective workflows. Rendered HTML, Plotly artifacts, and slides are intentional
outputs linked from their assignment documentation. This repository remains fully
standalone; no parent repository is required to understand or use it.
