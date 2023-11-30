from time import time
from math import log10

from src.randomizer import Randomizer, RandomizerCreator


class TableRandomizer(Randomizer):
    def __init__(self, values: list[int], seed: int, min: int, max: int):
        self.values = values
        self.current = seed % len(self.values)
        self.min = min
        self.max = max
        self.l = int(log10(self.max)) + 1
        self.limit = len(self.values)

    def get(self) -> int:
        num = self.min - 1

        while self.min > num or self.max < num:
            num = self.values[self.current]
            self.current = (self.current + 1) % self.limit

            for _ in range(self.l - 1):
                num = num * 10 + self.values[self.current]
                self.current = (self.current + 1) % self.limit

        return num


class TableRandomCreator(RandomizerCreator):
    def __init__(self, filename: str):
        file = open(filename, "r")
        content = file.read()
        file.close()
        self.values = list(map(lambda x: int(x), content[:-1]))

    def create(self, a: int, b: int) -> Randomizer:
        return TableRandomizer(self.values, int(time() * 1e6), a, b)

