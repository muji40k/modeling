from abc import ABC, abstractmethod

class RandomChecker(ABC):
    @abstractmethod
    def check(self, sequence: list[int]) -> float:
        pass

class Randomizer(ABC):
    @abstractmethod
    def get(self) -> int:
        pass

class RandomizerCreator(ABC):
    @abstractmethod
    def create(self, a: int, b: int) -> Randomizer:
        pass

