from dataclasses import dataclass
from typing import Callable

from misc.runthrough import runthrough_method, Matrix3Diagonal, InitialValues
from misc.interpolate import TableFunc
from misc.integrate import trapezoidal




@dataclass
class TaskHandle:
    lambda_f : Callable[[float], float]
    k_f      : Callable[[float], float]
    n        : float = 0
    r0       : float = 0
    r_max    : float = 0
    steps    : int   = 0
    t0       : float = 0
    sigma    : float = 0
    f_0      : float = 0
    alpha    : float = 0
    eps1     : float = 1e-4
    eps2     : float = 1e-4

@dataclass
class Result:
    radius : list[float]
    temperature : list[float]
    f1 : float
    f2 : float
    iter : int


def solve(handle : TaskHandle) -> Result:
    # step = (handle.r_max - handle.r0) / (handle.steps * handle.r_max)
    step = (handle.r_max - handle.r0) / handle.steps
    # step_0 = (handle.r_max - handle.r0) / handle.steps
    ir_max = 1 / handle.r_max
    origin_grid = [handle.r0 + i * step for i in range(handle.steps + 1)]
    # origin_grid = [handle.r0 + i * step_0 for i in range(handle.steps + 1)]
    grid = [i * ir_max for i in origin_grid]
    res = [handle.t0 for _ in origin_grid]

    irsqrh = 1 / (handle.r_max * handle.r_max * step)
    ir = 1 / handle.r_max
    basep = 4 * handle.n * handle.n * handle.sigma
    basef = basep * handle.t0 ** 4
    at0ir = handle.alpha * handle.t0 / handle.r_max

    matrix = Matrix3Diagonal(handle.steps - 1,
                             [0] * (handle.steps - 1),
                             [0] * (handle.steps - 1),
                             [0] * (handle.steps - 1),
                             [0] * (handle.steps - 1))
    start = InitialValues()
    end = InitialValues()
    f1 = 0
    f2 = 0

    run = True
    iter = 0

    while (run):
        for i in range(matrix.size):
            zm = (grid[i] + grid[i + 1]) / 2
            zp = (grid[i + 2] + grid[i + 1]) / 2
            v = (zp * zp - zm * zm) / 2
            kappam = (handle.lambda_f(res[i])
                      + handle.lambda_f(res[i + 1])) / 2
            kappap = (handle.lambda_f(res[i + 2])
                      + handle.lambda_f(res[i + 1])) / 2

            k = handle.k_f(res[i + 1])
            p = basep * k * res[i + 1] ** 3
            f = basef * k

            matrix.A[i] = irsqrh * zm * kappam
            matrix.C[i] = irsqrh * zp * kappap
            matrix.B[i] = matrix.A[i] + matrix.C[i] + p * v
            matrix.D[i] = f * v

        zhl = (grid[0] + grid[1]) / 2
        zhh = (grid[handle.steps] + grid[handle.steps - 1]) / 2

        kappal = (handle.lambda_f(res[0]) + handle.lambda_f(res[1])) / 2
        kappah = (handle.lambda_f(res[handle.steps])
                  + handle.lambda_f(res[handle.steps - 1])) / 2

        k0 = handle.k_f(res[0])
        k1 = handle.k_f(res[1])
        kN0 = handle.k_f(res[handle.steps - 1])
        kN1 = handle.k_f(res[handle.steps])

        p0 = basep * k0 * res[0] ** 3
        p1 = basep * k1 * res[1] ** 3
        pN0 = basep * kN0 * res[handle.steps - 1] ** 3
        pN1 = basep * kN1 * res[handle.steps] ** 3

        pl = (p0 + p1) / 2
        ph = (pN0 + pN1) / 2

        f0 = basef * k0
        f1 = basef * k1
        fN0 = basef * kN0
        fN1 = basef * kN1

        fl = (f0 + f1) / 2
        fh = (fN0 + fN1) / 2

        start.m = (kappal * irsqrh + step * pl / 8) * zhl + step * p0 * grid[0] / 4
        start.k = (step * pl / 8 - kappal * irsqrh) * zhl
        start.p = grid[0] * handle.f_0 * ir \
                  + step * (f0 * grid[0] + fl * zhl) / 4

        end.m = (-kappah * irsqrh + step * ph / 8) * zhh
        end.k = kappah * zhh * irsqrh + grid[handle.steps] * handle.alpha * ir \
                + step * (ph * zhh / 2 + pN1 * grid[handle.steps]) / 4
        end.p = at0ir * grid[handle.steps] + \
                + step * (fN1 * grid[handle.steps] + fh * zhh) / 4

        res_new = runthrough_method(matrix, start, end)
        c = 0

        for i in range(handle.steps + 1):
            if (abs((res[i] - res_new[i]) / res_new[i]) < handle.eps1):
                c += 1

        if (c == handle.steps + 1):
            run = False

        if (not run):
            f1 = handle.r0 * handle.f_0 \
                 - handle.r_max * handle.alpha * (res_new[-1] - handle.t0)

            # print(handle.r0 * handle.f_0)
            # print(handle.r_max * handle.alpha * (res_new[-1] - handle.t0))
            # print()

            tmp = [handle.k_f(res_new[i]) * (res_new[i] ** 4
                                             - handle.t0 ** 4)
                   * origin_grid[i] for i in range(handle.steps + 1)]

            f2 = 4 * handle.n * handle.n * handle.sigma \
                 * trapezoidal(handle.r0, handle.r_max, handle.steps,
                               TableFunc(origin_grid, tmp))

            if (1e-5 > abs(f1)):
                if (1e-5 < abs(f2)):
                    run = True
            elif (abs((f1 - f2) / f1) > handle.eps2):
                run = True

        print(iter, res_new[0])

        res = res_new
        iter += 1

    print(handle.r0 * handle.f_0)
    print(handle.r_max * handle.alpha * (res_new[-1] - handle.t0))
    print()

    return Result(origin_grid, res, f1, f2, iter)

