import sys
from src.misc import binary_search

def linear_interpolation(x : float, lx : list[float], ly : list[float]) -> float:
    if (len(lx) != len(ly)):
        return 0

    if (x < lx[0]):
        return ly[0]

    if (x > lx[-1]):
        return ly[-1]

    i = binary_search(lx, x)

    if (len(lx) <= i):
        return 0

    if (lx[i] > x):
        i -= 1

    if (sys.float_info.epsilon > abs(lx[i] - x)):
        return ly[i]

    return ly[i] + (ly[i + 1] - ly[i]) * (x - lx[i]) / (lx[i + 1] - lx[i])

class IncompatibleSizeNewtonValuesError(Exception):
    def __init__(self):
        super().__init__("Newton values have different sizes");

class NotEnoughValuesSlineError(Exception):
    def __init__(self):
        super().__init__("Newton should has at least 2 values");

class DisordedXValueNewtonError(Exception):
    def __init__(self):
        super().__init__("Newton x values have to be ascending ordered");

class ValueOutOfRangeNewtonError(Exception):
    def __init__(self):
        super().__init__("X coordinate is outside spline calculation range");


def newton_interpolation(x : float, lx : list[float], ly : list[float]) -> float:
    res : float = 0
    k = newton_get_coefficients(ly, lx)
    handle = 1

    for i in range(len(k)):
        res += handle * k[i]
        handle *= (x - lx[i])

    return res


def newton_get_coefficients(y: list[int | float], x: list[int | float]) -> list[float]:
    if len(x) != len(y):
        raise IncompatibleSizeNewtonValuesError

    k = y.copy()
    out = [k[0]]

    limit = len(x)
    i = 0
    while 1 != limit:

        j = 0
        while limit - 1 > j:
            k[j] = (k[j] - k[j + 1]) / (x[j] - x[j + i + 1])

            j += 1

        out.append(k[0])
        i += 1
        limit -= 1

    return out

