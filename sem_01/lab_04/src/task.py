from typing import Callable, Tuple

import math

from misc.runthrough import InitialValues
from src.common_task import BaseTaskHandle, BaseIterResult, BaseProgress
from misc.integrate import trapezoidal
from misc.interpolate import TableFunc


class funcFConst:
    def __init__(self, f_val : float):
        self.f_val = f_val

    def __call__(self, _ : float) -> float:
        return self.f_val


class funcF:
    def __init__(self, f_max : float, t_max : float, v : float):
        self.fracft = f_max / t_max * 1000
        self.it_max = 1 / t_max * 1000
        self.t = 1 / v
        self.v = v
        # self.fracft = f_max / t_max
        # self.it_max = 1 / t_max
        # self.t = 1 / v * 1000
        # self.v = v / 1000

    def __call__(self, t : float) -> float:
        t = self.t * math.modf(t * self.v)[0]

        return self.fracft * t * math.exp(1 - t * self.it_max)


class funcC:
    def __init__(self, a : float, b : float, c : float, m : float):
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def __call__(self, t : float) -> float:
        return self.a + self.b * t ** self.m - self.c / (t * t)


class TaskHandle(BaseTaskHandle):
    def __init__(self) -> None:
        self.lambda_f   : Callable[[float], float]
        self.k_f        : Callable[[float], float]
        self.f_f        : Callable[[float], float]
        self.c_f        : Callable[[float], float]

        self.n          : float = 0
        self.t0         : float = 0
        self.sigma      : float = 5.668e-12
        self.alpha      : float = 0

        self.r0         : float = 0
        self.r_max      : float = 0
        self.steps      : int   = 0

        self.time_steps   : int   = 0
        self.time_start   : float = 0
        self.time_end     : float = 0
        self.current_time : float = 0

        self.eps       : float = 0

                       #     x            time
    def start(self) -> Tuple[list[float], list[float]]:
        self.time_start /= 1000
        self.time_end /= 1000
        #
        self.step = (self.r_max - self.r0) / (self.steps * self.r_max)
        self.o_step = (self.r_max - self.r0) / self.steps
        self.time_step = (self.time_end - self.time_start) / self.time_steps

        self.ir = 1 / self.r_max
        self.origin_grid = [self.r0 + i * self.o_step for i in range(self.steps + 1)]
        self.grid = [i * self.ir for i in self.origin_grid]

        self.time_grid = [self.time_start + i * self.time_step
                          for i in range(self.time_steps + 1)]
        self.current_time = self.time_start

        self.irsqrh = 1 / (self.r_max * self.r_max * self.step)
        self.basep = 4 * self.n * self.n * self.sigma
        self.basef = self.basep * self.t0 ** 4
        self.at0ir = self.alpha * self.t0 / self.r_max

        self.current_f = self.f_f(self.current_time)
        self.r0current_f = self.r0 * self.current_f
        self.r_maxalpha = self.r_max * self.alpha

        self.prev = [self.t0 for _ in range(self.steps + 1)]
        self.prev_t = [self.t0 for _ in range(self.steps + 1)]

        # return self.origin_grid, self.time_grid
        return self.origin_grid, [1000 * i for i in self.time_grid]

    def step_t(self, f : list[float]) -> BaseIterResult:
        f1 = self.r0current_f - self.r_maxalpha * (f[-1] - self.t0)

        tmp = [self.k_f(f[i]) * (f[i] ** 4 - self.t0 ** 4)
               * self.origin_grid[i] for i in range(self.steps + 1)]

        f2 = self.basep * trapezoidal(self.r0, self.r_max, self.steps,
                                      TableFunc(self.origin_grid, tmp))

        self.prev_t = f
        self.prev = f
        self.current_time += self.time_step
        self.current_f = self.f_f(self.current_time)
        self.r0current_f = self.r0 * self.current_f

        return IterResult(True, f1, f2)

    def step_z(self, f : list[float]) -> BaseIterResult:
        terminate = False
        c = 0

        for i in range(self.steps + 1):
            if (abs((self.prev[i] - f[i]) / f[i]) < self.eps):
                c += 1

        if (c == self.steps + 1):
            terminate = True

        self.prev = f

        return IterResult(terminate, 0, 0)

    def getCoefficients(self, i : int) -> Tuple[float, float, float, float]:
        zm = (self.grid[i] + self.grid[i + 1]) / 2
        zp = (self.grid[i + 2] + self.grid[i + 1]) / 2
        v = (zp * zp - zm * zm) / 2

        kappam = (self.lambda_f(self.prev[i])
                  + self.lambda_f(self.prev[i + 1])) / 2
        kappap = (self.lambda_f(self.prev[i + 2])
                  + self.lambda_f(self.prev[i + 1])) / 2

        k = self.k_f(self.prev[i + 1])
        p = self.basep * k * self.prev[i + 1] ** 3 * self.time_step
        f = self.basef * k * self.time_step

        ch = self.c_f(self.prev[i + 1]) * self.step

        a = self.irsqrh * zm * kappam * self.time_step
        c = self.irsqrh * zp * kappap * self.time_step
        b = a + c + p * v + ch
        d = f * v + ch * self.prev_t[i + 1]

        return a, b, c, d

    def getStart(self) -> InitialValues:
        start = InitialValues()
        zhl = (self.grid[0] + self.grid[1]) / 2

        kappal = (self.lambda_f(self.prev[0]) + self.lambda_f(self.prev[1])) / 2

        k0 = self.k_f(self.prev[0])
        k1 = self.k_f(self.prev[1])

        p0 = self.basep * k0 * self.prev[0] ** 3
        p1 = self.basep * k1 * self.prev[1] ** 3
        pl = (p0 + p1) / 2

        f0 = self.basef * k0
        f1 = self.basef * k1
        fl = (f0 + f1) / 2

        ch = self.c_f(self.prev[0]) * self.step / 2

        start.m = ((kappal * self.irsqrh + self.step * pl / 8) * zhl + self.step * p0 * self.prev[0] / 4) * self.time_step + ch
        start.k = (self.step * pl / 8 - kappal * self.irsqrh) * zhl * self.time_step
        start.p = (self.grid[0] * self.current_f * self.ir \
                   + self.step * (f0 * self.grid[0] + fl * zhl) / 4) * self.time_step \
                   + ch * self.prev_t[0]

        return start

    # def getEnd(self) -> InitialValues:
    #     end = InitialValues()
    #     end.m = 0
    #     end.k = 1
    #     end.p = self.t0
    #     return end

    def getEnd(self) -> InitialValues:
        end = InitialValues()
        zhh = (self.grid[self.steps] + self.grid[self.steps - 1]) / 2

        kappah = (self.lambda_f(self.prev[self.steps])
                  + self.lambda_f(self.prev[self.steps - 1])) / 2

        kN0 = self.k_f(self.prev[self.steps - 1])
        kN1 = self.k_f(self.prev[self.steps])

        pN0 = self.basep * kN0 * self.prev[self.steps - 1] ** 3
        pN1 = self.basep * kN1 * self.prev[self.steps] ** 3
        ph = (pN0 + pN1) / 2

        fN0 = self.basef * kN0
        fN1 = self.basef * kN1
        fh = (fN0 + fN1) / 2

        ch = self.c_f(self.prev[self.steps]) * self.step / 2

        end.m = (-kappah * self.irsqrh + self.step * ph / 8) * zhh * self.time_step
        end.k = (kappah * zhh * self.irsqrh + self.grid[self.steps] * self.alpha * self.ir \
                 + self.step * (ph * zhh / 2 + pN1 * self.grid[self.steps]) / 4) * self.time_step \
                 + ch
        end.p = (self.at0ir * self.grid[self.steps] \
                 + self.step * (fN1 * self.grid[self.steps] + fh * zhh) / 4) * self.time_step \
                 + ch * self.prev_t[self.steps]

        return end


class IterResult(BaseIterResult):
    def __init__(self, terminate: bool = True, f1 : float = 0, f2 : float = 0):
        self.terminate = terminate
        self.f1 = f1
        self.f2 = f2

    def __bool__(self):
        return self.terminate


class Progress(BaseProgress):
    def __init__(self, handle : TaskHandle):
        self.cstep = 0
        self.imax = 1 / (handle.time_steps + 1)

    def step(self):
        self.cstep += 1

    def get(self) -> float:
        return self.cstep * self.imax

