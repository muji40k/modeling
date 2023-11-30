from typing import Callable
from polinomial import Polinomial

def integrate_positive(pol: Polinomial, x : float, y : float) -> Polinomial:
    res = Polinomial()
    powers = pol.powers()

    if (0 == len(powers)):
        res[0] = y
        return res

    if (0 > min(pol.powers())):
        return res

    for p in powers:
        res[p + 1] = pol[p] / (p + 1)

    res[0] = y - res(x)

    return res

def get_func(n : int, x0 : float, y0 : float, f : Callable[[Polinomial, Polinomial], Polinomial]) -> Polinomial:
    x = Polinomial()
    x[1] = 1

    out = Polinomial()
    out[0] = y0

    for _ in range(n):
        c = integrate_positive(f(x, out), 0, 0)
        out = c + float(y0 - c(x0))

    return out

class PicardFuncs:
    def __init__(self, x0 : float, y0 : float, n : int,
                 f : Callable[[Polinomial, Polinomial], Polinomial]):
        self._x0 : float = x0
        self._y0 : float = y0
        self._n : int = n
        self._f = f

    def __str__(self):
        return str(get_func(self._n, self._x0, self._y0, self._f))

    def setX0(self, x0 : float):
        self._x0 = x0

    def getX0(self):
        return self._x0

    def setY0(self, y0 : float):
        self._y0 = y0

    def getY0(self):
        return self._y0

    def setN(self, n : int):
        self._n = abs(n)

    def getN(self):
        return self._n

    def __call__(self, x : float, _ : float) -> float:
        return get_func(self._n, self._x0, self._y0, self._f)(x)

    x0 = property(getX0, setX0)
    y0 = property(getY0, setY0)
    n = property(getN, setN)

