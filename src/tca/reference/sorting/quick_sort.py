from tca.core.instrumentation import DirectProbe, Metrics, Probe
from tca.core.prng import PRNG


def quick_sort(
    values,
    metrics: Metrics | None = None,
    *,
    pivot: str = "first",
    recursion: str = "bounded",
    seed: int = 0,
) -> None:
    if pivot not in {"first", "quarter", "random"}:
        raise ValueError(f"unknown pivot strategy {pivot!r}")

    if recursion not in {"classic", "bounded"}:
        raise ValueError(f"unknown recursion strategy {recursion!r}")

    probe = DirectProbe() if metrics is None else Probe(metrics)
    prng = PRNG(seed)

    _quick_sort(values, 0, len(values) - 1, probe, pivot, recursion, prng)


def _choose_pivot(
    index_r: int,
    index_s: int,
    pivot: str,
    prng: PRNG,
) -> int:
    if pivot == "first":
        return index_r

    if pivot == "quarter":
        size = index_s - index_r + 1
        return index_r + size // 4

    if pivot == "random":
        size = index_s - index_r + 1
        return index_r + prng.randbelow(size)

    raise ValueError(f"unknown pivot strategy {pivot!r}")


def _partition(
    values, index_r: int, index_s: int, probe, pivot: str, prng: PRNG
) -> int:
    index_pivot = _choose_pivot(index_r, index_s, pivot, prng)
    probe.swap(values, index_r, index_pivot)  # move o pivô para x_r

    value_pivot = values[index_r]  # v = x_r
    index_i = index_r  # i = r
    index_j = index_s + 1  # j = s+1

    while True:  # repita {separação}
        index_i += 1  # i = i+1

        # até x_i >= v
        while index_i <= index_s and probe.lt(values[index_i], value_pivot):
            index_i += 1  # i = i+1

        index_j -= 1  # j = j-1

        while probe.lt(value_pivot, values[index_j]):  # até x_j <= v
            index_j -= 1  # j = j-1

        if index_j <= index_i:  # até j <= i
            break

        probe.swap(values, index_i, index_j)  # troque x_i com x_j

    probe.swap(values, index_r, index_j)  # troque x_r com x_j

    return index_j


def _quick_sort(
    values,
    index_r: int,
    index_s: int,
    probe,
    pivot: str,
    recursion: str,
    prng: PRNG,
) -> None:
    while index_r < index_s:  # enquanto s > r
        index_j = _partition(values, index_r, index_s, probe, pivot, prng)

        if recursion == "classic":
            _quick_sort(values, index_r, index_j - 1, probe, pivot, recursion, prng)
            _quick_sort(values, index_j + 1, index_s, probe, pivot, recursion, prng)
            return

        left_size = index_j - index_r
        right_size = index_s - index_j

        if left_size < right_size:
            _quick_sort(values, index_r, index_j - 1, probe, pivot, recursion, prng)
            index_r = index_j + 1  # continua iterativamente pela direita

        else:
            _quick_sort(values, index_j + 1, index_s, probe, pivot, recursion, prng)
            index_s = index_j - 1  # continua iterativamente pela esquerda
