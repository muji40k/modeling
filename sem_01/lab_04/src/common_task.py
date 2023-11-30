from dataclasses import dataclass
from typing import Tuple
from abc import ABC, abstractmethod

from misc.runthrough import runthrough_method, Matrix3Diagonal, InitialValues


class BaseIterResult:
    def __bool__(self):
        return True


class BaseTaskHandle(ABC):
    @abstractmethod
    def start(self) -> Tuple[list[float], list[float]]:
                       #     x            time
        pass

    @abstractmethod
    def step_t(self, f : list[float]) -> BaseIterResult:
        pass

    @abstractmethod
    def step_z(self, f : list[float]) -> BaseIterResult:
        pass

    @abstractmethod
    def getCoefficients(self, i : int) -> Tuple[float, float, float, float]:
        pass

    @abstractmethod
    def getStart(self) -> InitialValues:
        pass

    @abstractmethod
    def getEnd(self) -> InitialValues:
        pass

class BaseProgress(ABC):
    @abstractmethod
    def step(self):
        pass

    @abstractmethod
    def get(self) -> float:
        pass

@dataclass
class Result:
    radius : list[float]
    timeline : list[float]
    temperature : list[list[float]]
    res : list[BaseIterResult]


def solve(handle : BaseTaskHandle, progress : BaseProgress | None=None) -> Result:
    origin_grid, time_grid = handle.start()
    res : list[float] = []
    out : list[list[float]] = []
    iter_res : list[BaseIterResult] = []

    steps = len(origin_grid) - 2
    matrix = Matrix3Diagonal(steps, [0] * steps, [0] * steps, [0] * steps,
                             [0] * steps)

    for _ in time_grid:
        run = True

        while (run):
            for i in range(matrix.size):
                matrix.A[i], matrix.B[i], matrix.C[i], matrix.D[i] = \
                    handle.getCoefficients(i)

            res = runthrough_method(matrix, handle.getStart(), handle.getEnd())
            run = not (handle.step_z(res))

        iter_res.append(handle.step_t(res))
        out.append(res)

        if (progress):
            progress.step()

    return Result(origin_grid, time_grid, out, iter_res)

