from src.distribution import Distribution, DistributionCreator

class UniformDistribution(Distribution):
    def __init__(self, a, b):
        if (b < a):
            a, b = b, a

        self.a = a
        self.b = b
        self.value = 1 / (b - a)

    def cdf(self, x: float) -> float:
        if (x < self.a):
            return 0;

        if (x > self.b):
            return 1;

        return (x - self.a) * self.value

    def pdf(self, x: float) -> float:
        if (x < self.a or x > self.b):
            return 0;

        return self.value;

class UniformDistributionCreator(DistributionCreator):
    def create(self, kwargs: dict[str, float]) -> Distribution:
        a = kwargs["a"]
        b = kwargs["b"]

        return UniformDistribution(a, b)

