from dataclasses import dataclass


class ErrorIncompatibleListsMatrix3Diagonal(Exception):
    def __init__(self):
        super().__init__("Matrix presented with lists of different sizes");

@dataclass
class Matrix3Diagonal:
    size : int
    A    : list[int | float]
    B    : list[int | float]
    C    : list[int | float]
    D    : list[int | float]

@dataclass
class InitialValues:
    m : float = 0
    k : float = 0
    p : float = 0

@dataclass
class RunThroughCoefficient:
    k : float = 0
    b : float = 0


def _check_matrix_sizes(matrix: Matrix3Diagonal):
    if (not (matrix.size == len(matrix.A) == len(matrix.B)
             == len(matrix.C) == len(matrix.D))):
        raise ErrorIncompatibleListsMatrix3Diagonal


def runthrough_method(matrix: Matrix3Diagonal,
                      start: InitialValues,
                      end: InitialValues) -> list[float]:
    _check_matrix_sizes(matrix)

    result: list[float] = [0.0] * (matrix.size + 2)
    k = RunThroughCoefficient(-(start.k / start.m), start.p / start.m)
    run_coefficients: list[RunThroughCoefficient] = [k]

    for i in range(matrix.size):
        k = RunThroughCoefficient(
            matrix.C[i] / (matrix.B[i] - matrix.A[i] * k.k),
            (matrix.A[i] * k.b + matrix.D[i]) \
            / (matrix.B[i] - matrix.A[i] * k.k)
        )

        run_coefficients.append(k)

    print(len(run_coefficients))

    result[-1] = (end.p - end.m * k.b) / (end.k + end.m * k.k)

    for i in range(matrix.size, -1, -1):
        result[i] = run_coefficients[i].k * result[i + 1] \
                    + run_coefficients[i].b

    return result

