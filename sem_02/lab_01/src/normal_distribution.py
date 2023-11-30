from scipy.stats import norm
from math import pi, exp

from src.distribution import Distribution, DistributionCreator

class NormalDistribution(Distribution):
    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma

        self.scale = 1 / (self.sigma * (2 * pi) ** 0.5)

    def cdf(self, x: float) -> float:
        return norm.cdf(x, loc=self.mu, scale=self.sigma)

    def pdf(self, x: float) -> float:
        return self.scale * exp(-0.5 * ((x - self.mu) / self.sigma) ** 2)


class NormalDistributionCreator(DistributionCreator):
    def create(self, kwargs: dict[str, float]) -> Distribution:
        mu = kwargs["mu"]
        sigma = kwargs["sigma"]

        return NormalDistribution(mu, sigma)

