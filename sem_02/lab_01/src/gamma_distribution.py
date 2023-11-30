import sys
from math import exp

from src.distribution import Distribution, DistributionCreator

class GammaDistribution(Distribution):
    def __init__(self, k: int, _lambda: float):
        if (k < 0 or _lambda < sys.float_info.epsilon):
            raise BaseException;

        self.k = k
        self.lambda_val = _lambda
        factorial = 1;
        n = k - 1

        while (1 < n):
            factorial *= n
            n -= 1

        self.common = _lambda ** k / factorial

    def cdf(self, x: float) -> float:
        if (x < 0):
            return 0;

        lambdax = self.lambda_val * x
        val = 0
        current = 1
        i = 0

        while (self.k > i):
            i += 1
            val += current
            current *= lambdax / i

        return 1 - val * exp(-lambdax)


    def pdf(self, x: float) -> float:
        if (x < 0):
            return 0;

        return self.common * x ** (self.k - 1) * exp(-self.lambda_val * x)

class GammaDistributionCreator(DistributionCreator):
    def create(self, kwargs: dict[str, float]) -> Distribution:
        k = int(kwargs["k"])
        _lambda = kwargs["lambda"]

        return GammaDistribution(k, _lambda)

