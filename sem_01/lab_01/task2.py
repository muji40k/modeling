import math
import euler

def x(y : float) -> float:
    return math.e ** (y * y) - y * y / 2 - 1 / 2

def dxdy(y, x):
    return y * y * y + x * y * float(2)
# def dxdy(y : float, x : float) -> float:
#     return y * y * y + 2 * x * y

def x_next(y0 : float, y1 : float, x0 : float) -> euler.ImplicitEulerResult:
    dy = y1 - y0

    return euler.ImplicitEulerResult(True, (x0 + dy * y1 * y1 * y1) / (1 - 2 * y1 * dy))

