from typing import Callable

def runge_kutta(order : int, steps : int, x : float, x0 : float, y0 : list[float], *args : Callable[[float, list[float]], float], **kwargs) -> list[float]:
    if (1 == order):
        method = runge_kutta_1;
    elif (2 == order):
        method = runge_kutta_2;
    elif (4 == order):
        method = runge_kutta_4;
    else:
        return []

    h = (x - x0) / (steps - 1)
    out : list[float] = y0.copy()
    x = x0

    for _ in range(steps - 1):
        out = method(x, x + h, out, *args, **kwargs)

        if (not out):
            return []

        x += h

    return out


def runge_kutta_1(x1 : float, x2 : float, y : list[float], *args : Callable[[float, list[float]], float], **kwargs) -> list[float]:
    if (len(y) != len(args)):
        return []

    out = y.copy()

    for i, f in enumerate(args):
        out[i] += (x2 - x1) * f(x1, y)

    return out


def runge_kutta_2(x1 : float, x2 : float, y : list[float], *args : Callable[[float, list[float]], float], **kwargs) -> list[float]:
    if (len(y) != len(args)):
        return []

    if ("beta" not in kwargs.keys()):
        return []

    out = y.copy()

    beta = float(kwargs["beta"]);
    ib2 = 1 / (beta * beta)
    dx = x2 - x1
    x1dxib2 = x1 + dx * ib2

    k1 = [dx * f(x1, y) for f in args]
    y_k1 = [y[i] + k1[i] * ib2 for i in range(len(y))]

    for i, f in enumerate(args):
        out[i] += (1 - beta) * k1[i] + beta * dx * f(x1dxib2, y_k1)

    return out;


def runge_kutta_4(x1 : float, x2 : float, y : list[float], *args : Callable[[float, list[float]], float], **kwargs) -> list[float]:
    if (len(y) != len(args)):
        return []

    out = y.copy()

    dx = x2 - x1
    x1dxi2 = x1 + dx / 2
    x1dx = x1 + dx

    k1 = [dx * f(x1, y) for f in args]
    y_k1 = [y[i] + k1[i] / 2 for i in range(len(y))]
    k2 = [dx * f(x1dxi2, y_k1) for f in args]
    y_k2 = [y[i] + k2[i] / 2 for i in range(len(y))]
    k3 = [dx * f(x1dxi2, y_k2) for f in args]
    y_k3 = [y[i] + k3[i] for i in range(len(y))]

    for i, f in enumerate(args):
        k4 = dx * f(x1dx, y_k3)
        out[i] += (k1[i] + 2 * (k2[i] + k3[i]) + k4) / 6

    return out;

