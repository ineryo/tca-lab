class DirectProbe:
    @staticmethod
    def lt(
        left,
        right,
        *,
        indices: tuple[int, ...] = (),
        roles: tuple[str, ...] = (),
    ) -> bool:
        return left < right

    @staticmethod
    def swap(values, index_i: int, index_j: int) -> None:
        if index_i == index_j:
            return

        values[index_i], values[index_j] = values[index_j], values[index_i]

    @staticmethod
    def write(values, index: int, value, *, target: str | None = None) -> None:
        values[index] = value

    @staticmethod
    def event(
        kind: str,
        *,
        indices: tuple[int, ...] = (),
        values: tuple[object, ...] = (),
        **data,
    ) -> None:
        pass
