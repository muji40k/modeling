from typing import Callable
from dataclasses import dataclass

def evaluate_euler(y0 : float, x : list[float],
                   f : Callable[[float, float], float]) -> float:
    y = y0

    for i in range(1, len(x)):
        y += (x[i] - x[i - 1]) * f(x[i - 1], y)

    return y


@dataclass
class ImplicitEulerResult:
    valid : bool = False
    value : float = 0

def evaluate_implicit_euler(y0 : float, x : list[float],
                            f_impl : Callable[[float, float, float], ImplicitEulerResult]) -> ImplicitEulerResult:
                            #                  x_i    x_i+1  y_i
    y = ImplicitEulerResult(True, y0)
    i = 1

    while (len(x) > i and y.valid):
        y = f_impl(x[i - 1], x[i], y.value);
        i += 1

    return y


