MASK_64 = (1 << 64) - 1


class PRNG:
    def __init__(self, seed: int = 0) -> None:
        self.state = seed & MASK_64

    def next_uint64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK_64

        value = self.state
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK_64
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK_64
        value ^= value >> 31

        return value & MASK_64

    def randbelow(self, upper_bound: int) -> int:
        if upper_bound <= 0:
            raise ValueError("upper_bound must be greater than zero")

        threshold = ((1 << 64) - upper_bound) % upper_bound

        while True:
            value = self.next_uint64()

            if value >= threshold:
                return value % upper_bound
