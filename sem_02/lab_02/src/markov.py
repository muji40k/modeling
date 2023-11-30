import sys
import scipy


def solve(table : list[list[float]]) -> list[float]:
    matrix = []
    rs = [0 for _ in table]

    for i, line in enumerate(table[:-1]):
        matrix.append([table[j][i] for j in range(len(table))])
        matrix[i][i] -= sum(line)

    matrix.append([1 for _ in table])
    rs[-1] = 1

    return scipy.linalg.solve(matrix, rs)


class Derivative:
    def __init__(self, table : list[list[float]], state : int):
        self._lambda = [table[i][state] for i in range(len(table))]
        self._sum_out = -sum(table[state])
        self._state = state

    def __call__(self, probabilities : list[float]) -> float:
        return sum(map(lambda x, y: x * y, probabilities, self._lambda)) \
               + self._sum_out * probabilities[self._state]


def find_times(table, probabilities):
    p = [0 for _ in probabilities]
    for i in range(len(probabilities)):
        p[i] = (1 - probabilities[i]) / (probabilities[i] * sum(table[i]))

    print(p)


def check(derivatives : list[float], time : float,
          limit : float, eps : float, times : list[float]) -> bool:
    if (0 <= limit):
        return time < limit + sys.float_info.epsilon

    out : bool = False

    for i, derivative in enumerate(derivatives):
        if (eps < abs(derivative)):
            out = True

            if (0 <= times[i]):
                times[i] = -1
        elif (0 > times[i]):
            times[i] = time

    return out


def simulate(table : list[list[float]], step : float,
             initial_state : int=0, limit : float=-1,
             eps : float=sys.float_info.epsilon) -> tuple[list[list[float]], list[float]]:
    probabilities : list[list[float]] = [[1 if initial_state == i else 0 for i in range(len(table))]]
    current : list[float] = probabilities[0]
    times : list[float] = [-1 for _ in range(len(table))]
    time : float = 0
    run : bool = True

    derivative_functions = [Derivative(table, i) for i in range(len(table))]

    while run:
        time += step
        derivatives = list(map(lambda x : x(current), derivative_functions))
        current = list(map(lambda x, y: x + y * step, current, derivatives))
        probabilities.append(current)
        run = check(derivatives, time, limit, eps, times)

    return probabilities, times


