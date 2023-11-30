from typing import Callable


def trapezoidal(s : float, e : float, n : int, f : Callable[[float], float]) -> float:

    h = (e - s) / n
    x = s + h

    res = f(s) + f(e)

    for _ in range(1, n):
        res += 2 * f(x)
        x += h

    return res * h / 2

