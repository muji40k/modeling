from scipy.stats import chi2

from src.randomizer import RandomChecker

class Chi2RandomChecker(RandomChecker):
    def check(self, sequence: list[int]) -> float:
        values = {}
        n = len(sequence)
        range = max(sequence) - min(sequence) + 1

        for i in sequence:
            if i in values:
                values[i] += 1
            else:
                values[i] = 1

        sum_sqr = sum(map(lambda x : values[x] * values[x], values))
        val = range / n * sum_sqr - n

        return 1 - chi2.cdf(val, range - 1)

