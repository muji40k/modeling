import sys
from functools import singledispatchmethod

class _Polinomial:
    def __init__(self):
        self._k   : dict[int, float] = {}

    def __getitem__(self, p : int) -> float:
        if (p not in self._k.keys()):
            return 0

        return self._k[p]

    def __setitem__(self, p : int, value : float):
        self._k[p] = value

    def __str__(self) -> str:
        p = sorted(self._k.keys())
        out = []

        if 0 == len(p):
            return "0"

        for current in p:
            frame = "{}"
            value = self[current]

            if (0 > value):
                frame = "({})"

            if 0 == current and sys.float_info.epsilon < abs(value):
                out.append(frame.format("{:0.6g}".format(value)))
            elif sys.float_info.epsilon > abs(value - 1):
                out.append(frame.format("x^{}".format(current)))
            elif sys.float_info.epsilon < abs(value):
                out.append(frame.format("{:0.6g}x^{}".format(value, current)))

        return " + ".join(out)

    def __call__(self, x : float) -> float:
        res = 0

        for k in self._k.keys():
            res += self._k[k] * x ** k

        return res

    def copy(self):
        out = Polinomial()

        for p in self.powers():
            out[p] = self[p]

        return out

    def powers(self) -> list[int]:
        return [i for i in self._k.keys() if sys.float_info.epsilon < abs(self[i])]

class Polinomial(_Polinomial):
    @singledispatchmethod
    def __iadd__(self, other):
        raise NotImplementedError(f"Cannot add value of type {type(other)}")

    @__iadd__.register
    def _(self, other : float):
        self[0] += other

        return self

    @__iadd__.register
    def _(self, other : _Polinomial):
        for k in other._k.keys():
            self[k] += other._k[k]

        return self

    @singledispatchmethod
    def __add__(self, other):
        raise NotImplementedError(f"Cannot add value of type {type(other)}")

    @__add__.register
    def _(self, other : float):
        res = self.copy()
        res[0] += other

        return res

    @__add__.register
    def _(self, other : _Polinomial):
        res = Polinomial()

        for item in (other, self):
            for p in item._k.keys():
                res[p] += item._k[p]

        return res

    @singledispatchmethod
    def __isub__(self, other):
        raise NotImplementedError(f"Cannot sub value of type {type(other)}")

    @__isub__.register
    def _(self, other : float):
        self[0] -= other

        return self

    @__isub__.register
    def _(self, other : _Polinomial):
        for p in other._k.keys():
            self[p] -= other._k[p]

        return self

    @singledispatchmethod
    def __sub__(self, other):
        raise NotImplementedError(f"Cannot sub value of type {type(other)}")

    @__sub__.register
    def _(self, other : float):
        res = self.copy()
        res[0] -= other

        return res

    @__sub__.register
    def _(self, other : _Polinomial):
        res = Polinomial()

        for sign, item in enumerate((self, other)):
            sign = 1 - 2 * sign

            for p in item._k.keys():
                res[p] += sign * item._k[p]

        return res

    @singledispatchmethod
    def __imul__(self, other):
        raise NotImplementedError(f"Cannot mul value of type {type(other)}")

    @__imul__.register
    def _(self, other : float):
        for i in self._k.keys():
            self[i] *= other

        return self

    @__imul__.register
    def _(self, other : _Polinomial):
        k : dict[int, float] = {}

        for i in self._k.keys():
            for j in other._k.keys():
                if not i + j in k:
                    k[i + j] = 0

                k[i + j] += self[i] * other[j]

        self._k = k
        return self

    @singledispatchmethod
    def __mul__(self, other):
        raise NotImplementedError(f"Cannot mul value of type {type(other)}")

    @__mul__.register
    def _(self, other : float):
        res = self.copy()

        for i in res._k.keys():
            res[i] *= other

        return res

    @__mul__.register
    def _(self, other : _Polinomial):
        res = Polinomial()

        for i in self._k.keys():
            for j in other._k.keys():
                res[i + j] += self[i] * other[j]

        return res

    def __pow__(self, power : int):
        power = abs(power)
        res = Polinomial()
        res[0] = 1

        for _ in range(power):
            res *= self

        return res

