from typing import Callable, Tuple
from abc import ABC, abstractmethod

import math

from misc.runthrough import InitialValues
from src.common_task3 import BaseTaskHandle, BaseIterResult, BaseProgress


def get_cmp_diff(eps : float) -> Callable[[float, float], bool]:
    def cmp_diff(a : float, b : float) -> bool:
        return abs(a - b) > eps

    return cmp_diff

def get_cmp_absolute(eps : float) -> Callable[[float, float], bool]:
    def cmp_absolute(a : float, b : float) -> bool:
        if (abs(b) < 1e-8):
            if (abs(a) > 1e-8):
                return True
        elif (abs((a - b) / b) > eps):
            return True

        return False

    return cmp_absolute


class funcLambda:
    def __init__(self, a : float, b : float, c : float, m : float):
        self.m = m

        self.ab = a * b
        self.ac = a * c

    def __call__(self, t : float) -> float:
        return self.ab + self.ac * t ** self.m

class funcFSmooth:
    def __init__(self, f_0 : float, x_0 : float, y_0 : float):
        self.x_0 = x_0
        self.y_0 = y_0
        self.f_0 = f_0

    def __call__(self, x : float, y : float) -> float:
        x -= self.x_0
        y -= self.y_0

        return self.f_0 / ((x * x + 1) * (y * y + 1))

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
    pass

class InitialValuesTask(ABC):
    @abstractmethod
    def get(self, handle: TaskHandle, i : int) -> InitialValues:
        pass


class TaskHandle(BaseTaskHandle):
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

        self.timestep : float = 0

        self.eps_time  : float = 0
        self.eps_lin   : float = 0

    @classmethod
    def check(cls, origin : list[list[float]], res : list[list[float]], cmp : Callable[[float, float], bool]) -> bool:
        terminate = True
        i = 0

        while (terminate and i < len(origin)):
            j = 0

            while (terminate and j < len(origin[i])):
                if (cmp(origin[i][j], res[i][j])):
                    terminate = False

                j += 1

            i += 1

        return terminate

    def start(self) -> Tuple[list[float], list[float]]:
        width = self.x_max - self.x_0
        height = self.z_max - self.z_0
        self.x_step = width / self.x_steps
        self.z_step = height / self.z_steps

        self.ix_stepsqr = 1 / (2 * self.x_step * self.x_step)
        self.iz_stepsqr = 1 / (2 * self.z_step * self.z_step)

        self.x = [self.x_0 + i * self.x_step for i in range(self.x_steps + 1)]
        self.z = [self.z_0 + i * self.z_step for i in range(self.z_steps + 1)]

        self.t_mem =     [[self.t_0 for _ in range(self.x_steps + 1)]
                          for _ in range(self.z_steps + 1)]
        self.t_prev =    [[self.t_0 for _ in range(self.x_steps + 1)]
                          for _ in range(self.z_steps + 1)]
        self.t_current = [[self.t_0 for _ in range(self.x_steps + 1)]
                          for _ in range(self.z_steps + 1)]
        self.t_tmp = []

        self.htimestep = self.timestep / 2
        self.eps_time *= self.timestep
        self.last_diff = 0

        return self.x, self.z

    def step_half(self, tmp : list[list[float]]) -> None:
        self.t_tmp = [i.copy() for i in tmp]

    def step_full(self, full : list[list[float]]) -> BaseIterResult:
        terminate = self.check(self.t_current, full,
                               get_cmp_absolute(self.eps_lin))
        self.t_current = [i.copy() for i in full]

        return IterResult(terminate)

    def step_main(self, full : list[list[float]]) -> BaseIterResult:
        terminate = self.check(self.t_prev, full,
                               get_cmp_diff(self.eps_time))
        self.t_mem = self.t_prev
        self.t_prev = [i.copy() for i in full]
        self.t_current = [i.copy() for i in full]

        return IterResult(terminate)

    def getCoefficients_half(self, i : int, j : int) -> Tuple[float, float, float, float]:
        kappavh = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j + 2][i + 1]) / 2)
        kappavl = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j][i + 1]) / 2)
        kappaxh = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j + 1][i + 2]) / 2)
        kappaxl = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j + 1][i]) / 2)

        return kappaxl * self.ix_stepsqr * self.htimestep,                   \
               (kappaxl + kappaxh) * self.ix_stepsqr * self.htimestep + 1,   \
               kappaxh * self.ix_stepsqr * self.htimestep,                   \
               ((kappavl * self.t_current[j][i + 1]
                 - (kappavl + kappavh) * self.t_current[j + 1][i + 1]
                 + kappavh * self.t_current[j + 2][i + 1]) * self.iz_stepsqr
                + self.f_f(self.x[i + 1], self.z[j + 1])) * self.htimestep   \
               + self.t_current[j + 1][i + 1]

    def getCoefficients_full(self, i : int, j : int) -> Tuple[float, float, float, float]:
        kappavh = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j + 2][i + 1]) / 2)
        kappavl = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j][i + 1]) / 2)
        kappaxh = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j + 1][i + 2]) / 2)
        kappaxl = self.lambda_f((self.t_current[j + 1][i + 1]
                                 + self.t_current[j + 1][i]) / 2)

        return kappavl * self.iz_stepsqr * self.htimestep,                 \
               (kappavl + kappavh) * self.iz_stepsqr * self.htimestep + 1, \
               kappavh * self.iz_stepsqr * self.htimestep,                 \
               ((kappaxl * self.t_tmp[j + 1][i]
                 - (kappaxl + kappaxh) * self.t_tmp[j + 1][i + 1]
                 + kappaxh * self.t_tmp[j + 1][i + 2]) * self.ix_stepsqr
                + self.f_f(self.x[i + 1], self.z[j + 1])) * self.htimestep \
               + self.t_tmp[j + 1][i + 1]

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


class Progress(BaseProgress):
    def __init__(self):
        self.prev    : list[list[float]] = []
        self.current : list[list[float]] = []
        self.timestep : float = 0

    def reset(self, handle : TaskHandle) -> None:
        self.step(handle)
        self.timestep = handle.timestep

    def step(self, handle : TaskHandle) -> None:
        self.prev = handle.t_mem
        self.current = handle.t_prev


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


class InitialValuesIIOrder(InitialValuesTask):
    pass

class TaskInitialValuesIIOrder(InitialValuesIIOrder):
    def __init__(self, f0 : float, step_f : Callable[[TaskHandle], float],
                 address : Callable[[TaskHandle, int, int], float]):
        self.f0 = f0
        self.step : Callable[[TaskHandle], float] = step_f
        self.address : Callable[[TaskHandle, int, int], float] = address

    def get(self, handle : TaskHandle, i : int) -> InitialValues:
        kappa = handle.lambda_f((self.address(handle, 0, i)
                                 + self.address(handle, 1, i)) / 2)

        start = InitialValues()
        start.p = self.f0 * self.step(handle) / kappa

        return start

class TaskStartValuesIIOrder(TaskInitialValuesIIOrder):
    def __init__(self, f0 : float, step_f : Callable[[TaskHandle], float],
                 address : Callable[[TaskHandle, int, int], float]):
        super().__init__(f0, step_f, address)

    def get(self, handle : TaskHandle, i : int) -> InitialValues:
        start = super().get(handle, i)

        start.m = 1
        start.k = -1

        return start

class TaskEndValuesIIOrder(TaskInitialValuesIIOrder):
    def __init__(self, f0 : float, step_f : Callable[[TaskHandle], float],
                 address : Callable[[TaskHandle, int, int], float]):
        super().__init__(f0, step_f, address)

    def get(self, handle : TaskHandle, i : int) -> InitialValues:
        start = super().get(handle, i)

        start.m = -1
        start.k = 1

        return start

class TaskXStartValuesIIOrder(TaskStartValuesIIOrder):
    def __init__(self, f0 : float):
        super().__init__(f0, lambda x : x.x_step, lambda x, i, j : x.t_current[i][j])

class TaskXEndValuesIIOrder(TaskEndValuesIIOrder):
    def __init__(self, f0 : float):
        super().__init__(f0, lambda x : x.x_step, lambda x, i, j : x.t_current[x.x_steps - 2 + i][j])

class TaskVStartValuesIIOrder(TaskStartValuesIIOrder):
    def __init__(self, f0 : float):
        super().__init__(f0, lambda x : x.z_step, lambda x, i, j : x.t_current[j][i])

class TaskVEndValuesIIOrder(TaskEndValuesIIOrder):
    def __init__(self, f0 : float):
        super().__init__(f0, lambda x : x.z_step, lambda x, i, j : x.t_current[j][x.z_steps - 2 + i])


class InitialValuesIIIOrder(InitialValuesTask):
    pass

class TaskInitialValuesIIIOrder(InitialValuesIIIOrder):
    def __init__(self, alpha : float, u0 : float, step_f : Callable[[TaskHandle], float],
                 address : Callable[[TaskHandle, int, int], float]):
        self.alpha = alpha
        self.u0alpha = - u0 * alpha
        self.step : Callable[[TaskHandle], float] = step_f
        self.address : Callable[[TaskHandle, int, int], float] = address

    def kappa(self, handle : TaskHandle, i : int):
        return handle.lambda_f((self.address(handle, 0, i)
                                + self.address(handle, 1, i)) / 2)

    def get(self, _ : TaskHandle, __ : int) -> InitialValues:
        start = InitialValues()
        start.p = self.u0alpha

        return start

class TaskStartValuesIIIOrder(TaskInitialValuesIIIOrder):
    def __init__(self, alpha : float, u0 : float, step_f : Callable[[TaskHandle], float],
                 address : Callable[[TaskHandle, int, int], float]):
        super().__init__(alpha, u0, step_f, address)

    def get(self, handle : TaskHandle, i : int) -> InitialValues:
        start = super().get(handle, i)
        kappaistep = self.kappa(handle, i) / self.step(handle)

        start.m = -kappaistep - self.alpha
        start.k = kappaistep

        return start

class TaskEndValuesIIIOrder(TaskInitialValuesIIIOrder):
    def __init__(self, alpha : float, u0 : float, step_f : Callable[[TaskHandle], float],
                 address : Callable[[TaskHandle, int, int], float]):
        super().__init__(alpha, u0, step_f, address)

    def get(self, handle : TaskHandle, i : int) -> InitialValues:
        start = super().get(handle, i)
        kappaistep = self.kappa(handle, i) / self.step(handle)

        start.m = kappaistep
        start.k = -kappaistep - self.alpha

        return start

class TaskXStartValuesIIIOrder(TaskStartValuesIIIOrder):
    def __init__(self, alpha : float, u0 : float):
        super().__init__(alpha, u0, lambda x : x.x_step, lambda x, i, j : x.t_current[i][j])

class TaskXEndValuesIIIOrder(TaskEndValuesIIIOrder):
    def __init__(self, alpha : float, u0 : float):
        super().__init__(alpha, u0, lambda x : x.x_step, lambda x, i, j: x.t_current[x.x_steps - 2 + i][j])

class TaskVStartValuesIIIOrder(TaskStartValuesIIIOrder):
    def __init__(self, alpha : float, u0 : float):
        super().__init__(alpha, u0, lambda x : x.z_step, lambda x, i, j: x.t_current[j][i])

class TaskVEndValuesIIIOrder(TaskEndValuesIIIOrder):
    def __init__(self, alpha : float, u0 : float):
        super().__init__(alpha, u0, lambda x : x.z_step, lambda x, i, j : x.t_current[j][x.z_steps - 2 + i])

