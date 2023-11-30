from typing import Callable

def evaluate_picard(x0 : float, y0 : float, x : float,
                    f_int : Callable[[float, float], float]) -> float:
                    #                 x      y0
    return y0 + f_int(x, y0) - f_int(x0, y0);

