class DirectProbe:
    @staticmethod
    def lt(left, right) -> bool:
        return left < right

    @staticmethod
    def swap(values, index_i: int, index_j: int) -> None:
        if index_i == index_j:
            return

        values[index_i], values[index_j] = (
            values[index_j],
            values[index_i],
        )
