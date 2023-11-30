from typing import Callable, Tuple

import math

from misc.runthrough import InitialValues
from src.common_task2 import BaseTaskHandle, BaseIterResult

from abc import ABC, abstractmethod

class TaskHandle(BaseTaskHandle):
    pass

class InitialValuesTask(ABC):
    @abstractmethod
    def get(self, handle: TaskHandle, i : int) -> InitialValues:
        pass


class InitialValuesIOrder(InitialValuesTask):
    def __init__(self, m : float, k : float, p : float):
        self.value = InitialValues(m, k, p)

    def get(self, _ : TaskHandle, __ : int) -> InitialValues:
        return self.value

class StartValuesIOrder(InitialValuesIOrder):
    def __init__(self, u : float):
        super().__init__(1, 0, u)

class EndValuesIOrder(InitialValuesIOrder):
    def __init__(self, u : float):
        super().__init__(0, 1, u)


# class InitialValuesIIOrder(InitialValuesTask):
#     def __init__(self, f0 : float, lambda_f : Callable[[float], float]):
#         self.f0 = f0
#         self.lambda_f = lambda_f
#  
# class StartValuesIIOrder(InitialValuesIIOrder):
#     def __init__(self, f0 : float, lambda_f : Callable[[float], float]):
#         super().__init__(f0, lambda_f)
#  
#     def get(self, handle : TaskHandle) -> InitialValues:
#  
# class EndValuesIIOrder(InitialValuesIIOrder):
#     def __init__(self, f0 : float, lambda_f : Callable[[float], float]):
#         super().__init__(f0, lambda_f)
#  
#     def get(self, handle : TaskHandle) -> InitialValues:
#         pass


class funcLambda:
    def __init__(self, a : float, b : float, c : float, m : float):
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def __call__(self, t : float) -> float:
        return self.a * (self.b + self.c * t ** self.m)

class funcF:
    def __init__(self, f_0 : float, beta : float, x_0 : float, y_0 : float):
        self.f_0 = f_0
        self.beta = -beta
        self.x_0 = x_0
        self.y_0 = y_0

    def __call__(self, x : float, y : float) -> float:
        x -= self.x_0
        y -= self.y_0
        return self.f_0 * math.exp(self.beta * x * x * y * y)


class TaskHandle(BaseTaskHandle):
    # I = 1
    def __init__(self) -> None:
        self.lambda_f   : Callable[[float], float]
        self.f_f        : Callable[[float, float], float]

        self.bottom : InitialValuesTask | None = None
        self.top    : InitialValuesTask | None = None
        self.left   : InitialValuesTask | None = None
        self.right  : InitialValuesTask | None = None

        self.t_0   : float = 0

        self.x_0   : float = 0
        self.x_max : float = 0
        self.z_0   : float = 0
        self.z_max : float = 0

        self.x_steps : int = 0
        self.z_steps : int = 0

        self.eps       : float = 0

    def start(self) -> Tuple[list[float], list[float]]:
        width = self.x_max - self.x_0
        height = self.z_max - self.z_0
        self.x_step = width / self.x_steps
        self.z_step = height / self.z_steps

        self.ix_stepsqr = 1 / (2 * self.x_step * self.x_step)
        self.iz_stepsqr = 1 / (2 * self.z_step * self.z_step)

        self.x = [self.x_0 + i * self.x_step for i in range(self.x_steps + 1)]
        self.z = [self.z_0 + i * self.z_step for i in range(self.z_steps + 1)]

        self.t      = [[self.t_0 for _ in range(self.x_steps + 1)] for _ in range(self.z_steps + 1)]
        self.t_half = [[self.t_0 for _ in range(self.x_steps + 1)] for _ in range(self.z_steps + 1)]
        self.t_tmp  = [[self.t_0 for _ in range(self.x_steps + 1)] for _ in range(self.z_steps + 1)]

        return self.x, self.z

    def startHalf(self) -> None:
        self.t_half = [i.copy() for i in self.t_tmp]

    @classmethod
    def check(cls, origin : list[list[float]], res : list[list[float]], eps : float) -> bool:
        terminate = True
        i = 0

        while (terminate and i < len(origin)):
            j = 0

            while (terminate and j < len(origin[i])):
                if (abs(res[i][j]) < 1e-8):
                    if (abs(origin[i][j]) > 1e-8):
                        terminate = False
                elif (abs((origin[i][j] - res[i][j]) / res[i][j]) > eps):
                    terminate = False

                j += 1

            i += 1

        return terminate

    def step_half(self, tmp : list[list[float]]) -> BaseIterResult:
        terminate = self.check(self.t_tmp, tmp, self.eps)

        self.t_tmp = [i.copy() for i in tmp]

        return IterResult(terminate)

    def step_full(self, full : list[list[float]]) -> BaseIterResult:
        terminate = self.check(self.t_tmp, full, self.eps)

        self.t_tmp = [i.copy() for i in full]

        return IterResult(terminate)

    I = 2

    def step_main(self, full : list[list[float]]) -> BaseIterResult:
        # terminate = self.check(self.t, full, self.eps)

        self.t_tmp = [i.copy() for i in full]
        self.t = [i.copy() for i in full]

        # return IterResult(terminate)
        self.I -= 1
        return IterResult(0 == self.I)

    def getCoefficients_half(self, i : int, j : int) -> Tuple[float, float, float, float]:
        kappaxh = self.lambda_f((self.t_tmp[i + 1][j + 1] + self.t_tmp[i + 2][j + 1]) / 2)
        kappaxl = self.lambda_f((self.t_tmp[i + 1][j + 1] + self.t_tmp[i][j + 1]) / 2)
        kappavh = self.lambda_f((self.t[i + 1][j + 1] + self.t[i + 1][j + 2]) / 2)
        kappavl = self.lambda_f((self.t[i + 1][j + 1] + self.t[i + 1][j]) / 2)

        return kappaxl * self.ix_stepsqr,             \
               (kappaxl + kappaxh) * self.ix_stepsqr, \
               kappaxh * self.ix_stepsqr,             \
               (kappavl * self.t[i + 1][j] - (kappavl + kappavh) * self.t[i + 1][j + 1] + kappavh * self.t[i + 1][j + 2]) * self.iz_stepsqr + self.f_f(self.x[i + 1], self.z[j + 1])

        # return self.z_step * self.z_step, 2 * self.z_step * self.z_step, self.z_step * self.z_step, \
                #        self.x_step * self.x_step \
                #        * (self.t[j][i + 1] - 2 * self.t[j + 1][i + 1] + self.t[j + 2][i + 1] \
                #           + self.f_f(self.x[i + 1], self.z[j + 1]) \
                #             / self.lambda_f(self.t[j + 1][i + 1]) \
                #             * self.z_step * self.z_step)

    def getCoefficients_full(self, i : int, j : int) -> Tuple[float, float, float, float]:
        kappaxh = self.lambda_f((self.t_half[i + 1][j + 1] + self.t_half[i + 2][j + 1]) / 2)
        kappaxl = self.lambda_f((self.t_half[i + 1][j + 1] + self.t_half[i][j + 1]) / 2)
        kappavh = self.lambda_f((self.t_tmp[i + 1][j + 1] + self.t_tmp[i + 1][j + 2]) / 2)
        kappavl = self.lambda_f((self.t_tmp[i + 1][j + 1] + self.t_tmp[i + 1][j]) / 2)

        return kappavl * self.iz_stepsqr,             \
               (kappavl + kappavh) * self.iz_stepsqr, \
               kappavh * self.iz_stepsqr,             \
               (kappaxl * self.t_half[i][j + 1] - (kappaxl + kappaxh) * self.t_half[i + 1][j + 1] + kappaxh * self.t_half[i + 2][j + 1]) * self.ix_stepsqr + self.f_f(self.x[i + 1], self.z[j + 1])

        # return self.x_step * self.x_step, 2 * self.x_step * self.x_step, self.x_step * self.x_step, \
                #        self.z_step * self.z_step \
                #        * (self.t_tmp[j + 1][i] - 2 * self.t_tmp[j + 1][i + 1] \
                #           + self.t_tmp[j + 1][i + 2] + self.f_f(self.x[i + 1], self.z[j + 1]) \
                #                                    / self.lambda_f(self.t[j + 1][i + 1]) \
                #                                    * self.x_step * self.x_step)

    def getLeft(self, v : int) -> InitialValues:
        return self.left.get(self, v)

    def getRight(self, v : int) -> InitialValues:
        return self.right.get(self, v)

    def getBottom(self, h : int) -> InitialValues:
        return self.bottom.get(self, h)

    def getTop(self, h : int) -> InitialValues:
        return self.top.get(self, h)


class IterResult(BaseIterResult):
    def __init__(self, terminate: bool = True):
        self.terminate = terminate

    def __bool__(self):
        return self.terminate

