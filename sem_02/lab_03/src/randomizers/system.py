import random

from src.randomizer import Randomizer, RandomizerCreator


class SystemRandomizer(Randomizer):
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def get(self) -> int:
        return random.randint(self.a, self.b)


class SystemRandomizerCreator(RandomizerCreator):
    def create(self, a: int, b: int) -> Randomizer:
        return SystemRandomizer(a, b)

