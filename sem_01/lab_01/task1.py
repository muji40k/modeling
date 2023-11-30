import math
import euler

def x(y : float) -> float:
    return 3 * math.e ** y - y * y - 2 * y - 2

def dxdy(y, x):
    return x + y ** 2
# def dxdy(y : float, x : float) -> float:
#     return y ** 2 + x

def x_next(y0 : float, y1 : float, x0 : float) -> euler.ImplicitEulerResult:
    dy = y1 - y0

    return euler.ImplicitEulerResult(True, (x0 + dy * y1 * y1) / (1 - dy))

