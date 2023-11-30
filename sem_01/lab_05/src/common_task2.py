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
                       #     x            y
        pass

    @abstractmethod
    def startHalf(self) -> None:
        pass

    @abstractmethod
    def step_half(self, tmp : list[list[float]]) -> BaseIterResult:
        pass

    @abstractmethod
    def step_full(self, full : list[list[float]]) -> BaseIterResult:
        pass

    @abstractmethod
    def step_main(self, full : list[list[float]]) -> BaseIterResult:
        pass

    @abstractmethod
    def getCoefficients_half(self, i : int, j : int) -> Tuple[float, float, float, float]:
        pass

    @abstractmethod
    def getCoefficients_full(self, i : int, j : int) -> Tuple[float, float, float, float]:
        pass

    @abstractmethod
    def getLeft(self, v : int) -> InitialValues:
        pass

    @abstractmethod
    def getRight(self, v : int) -> InitialValues:
        pass

    @abstractmethod
    def getBottom(self, h : int) -> InitialValues:
        pass

    @abstractmethod
    def getTop(self, h : int) -> InitialValues:
        pass


@dataclass
class Result:
    x : list[float]
    y : list[float]
    temperature : list[list[float]]
    res : list[BaseIterResult]


def solve(handle : BaseTaskHandle) -> Result:
    x, y = handle.start()
    res : list[list[float]] = [[0 for _ in range(len(x))] for _ in range(len(y))]
    iter_res : list[BaseIterResult] = []

    steps_h = len(x) - 2
    matrix_h = Matrix3Diagonal(steps_h, [0] * steps_h, [0] * steps_h,
                                        [0] * steps_h, [0] * steps_h)
    steps_v = len(y) - 2
    matrix_v = Matrix3Diagonal(steps_v, [0] * steps_v, [0] * steps_v,
                                        [0] * steps_v, [0] * steps_v)

    run = True

    while (run):
        run_inner = True

        while (run_inner):
            for j in range(matrix_v.size):
                for i in range(matrix_h.size):
                    matrix_h.A[i], matrix_h.B[i], matrix_h.C[i], matrix_h.D[i] = \
                        handle.getCoefficients_half(i, j)

                res[j + 1] = runthrough_method(matrix_h, handle.getLeft(j),
                                               handle.getRight(j))

            for i in range(matrix_h.size + 2):
                bottom = handle.getBottom(i)
                top = handle.getTop(i)
                res[0][i] = (bottom.p - bottom.k * res[1][i]) / bottom.m
                res[steps_v + 1][i] = (top.p - top.m * res[steps_v][i]) \
                                      / top.k

            run_inner = not handle.step_half(res)

        handle.startHalf()
        run_inner = True

        while (run_inner):
            for i in range(matrix_h.size):
                for j in range(matrix_v.size):
                    matrix_v.A[j], matrix_v.B[j], matrix_v.C[j], matrix_v.D[j] = \
                        handle.getCoefficients_full(i, j)

                tmp = runthrough_method(matrix_v, handle.getBottom(i),
                                        handle.getTop(i))

                for j in range(matrix_v.size + 2):
                    res[j][i + 1] = tmp[j]

            for j in range(matrix_v.size + 2):
                left = handle.getLeft(j)
                right = handle.getRight(j)
                res[j][0] = (left.p - left.k * res[j][1]) / left.m
                res[j][steps_h + 1] = (right.p - right.m * res[j][steps_h]) \
                                      / right.k

            run_inner = not handle.step_full(res)

        iter = handle.step_main(res)
        run = not (iter)
        iter_res.append(iter)

    return Result(x, y, res, iter_res)


