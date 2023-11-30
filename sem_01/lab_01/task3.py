import sys
import euler

def dydx(x, y):
    return x * x + y * y
# def dydx(x : float, y : float) -> float:
#     return x * x + y * y

class y_next:
    def __init__(self, sign):
        self._sign = 0
        self.setSign(sign)

    def setSign(self, sign):
        if (0 <= sign):
            self._sign = 1
        else:
            self._sign = -1

    def __call__(self, x0 : float, x1 : float, y0 : float) -> euler.ImplicitEulerResult:
        dx = x1 - x0
        res = euler.ImplicitEulerResult()

        d = 1 - 4 * dx * (y0 + dx * x1 * x1)

        if (-sys.float_info.epsilon > d):
            return res

        if (sys.float_info.epsilon > d):
            res = euler.ImplicitEulerResult(True, 1 / (2 * dx))
        else:
            res = euler.ImplicitEulerResult(True, (1 + self._sign * d ** 0.5) / (2 * dx))

        return res


