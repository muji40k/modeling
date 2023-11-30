from time import time

from src.randomizer import Randomizer, RandomizerCreator


class LinearCongruentRandomizer(Randomizer):
    def __init__(self, a: int, c: int, m: int, i: int, min: int, max: int):
        self.a = a
        self.c = c
        self.m = m

        self.current = i % self.m

        self.min = min
        self.rng = max - min + 1

    def get(self) -> int:
        self.current = (self.a * self.current + self.c) % self.m

        return self.min \
               + int(round(self.rng * (self.current / (self.m - 1)) - 0.5, 0))


class LinearCongruentRandomCreator(RandomizerCreator):
    def __init__(self, a: int, c: int, m: int):
        self.a = a
        self.c = c
        self.m = m

    def create(self, a: int, b: int) -> Randomizer:
        return LinearCongruentRandomizer(self.a, self.c, self.m,
                                         int(time() * 1e6), a, b)

