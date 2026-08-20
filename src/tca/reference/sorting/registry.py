from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from types import MappingProxyType

SortFunction = Callable[..., None]


def _discover_sorting_algorithms() -> dict[str, SortFunction]:
    algorithms: dict[str, SortFunction] = {}

    package_directory = Path(__file__).parent

    for path in sorted(package_directory.glob("*_sort.py")):
        module_name = path.stem

        if module_name.startswith("_"):
            continue

        method = module_name.removesuffix("_sort")

        module = import_module(f"{__package__}.{module_name}")

        function = getattr(
            module,
            module_name,
            None,
        )

        if not callable(function):
            raise RuntimeError(
                f"{module_name}.py must define " f"a callable named {module_name}"
            )

        algorithms[method] = function

    return algorithms


_SORTING_ALGORITHMS = _discover_sorting_algorithms()

SORTING_ALGORITHMS = MappingProxyType(_SORTING_ALGORITHMS)


def available_sorting_algorithms() -> tuple[str, ...]:
    return tuple(SORTING_ALGORITHMS)


def get_sorting_algorithm(
    method: str,
) -> SortFunction:
    try:
        return SORTING_ALGORITHMS[method]
    except KeyError as error:
        available = ", ".join(available_sorting_algorithms())

        raise ValueError(
            f"unknown sorting algorithm {method!r}; " f"available methods: {available}"
        ) from error
