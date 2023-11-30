from abc import ABC, abstractmethod

class Distribution(ABC):
    @abstractmethod
    def cdf(self, x: float) -> float:
        pass

    @abstractmethod
    def pdf(self, x: float) -> float:
        pass

class DistributionCreator(ABC):
    @abstractmethod
    def create(self, kwargs: dict[str, float]) -> Distribution:
        pass

