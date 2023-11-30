import math


ASCENDING  = 0
DESCENDING = 1
DISORDERED = 2

EPS = 1e-8


def is_ordered(lst: list[int | float]) -> int:
    if (len(lst) < 1):
        return DISORDERED

    order = DISORDERED
    if lst[0] < lst[1]:
        order = ASCENDING
    elif lst[0] > lst[1]:
        order = DESCENDING

    i = 1;
    while len(lst) > i and DISORDERED != order:
        if ASCENDING == order and lst[0] > lst[1]:
            order = DISORDERED
        elif DESCENDING == order and lst[0] < lst[1]:
            order = DISORDERED
        elif EPS > abs(lst[1] - lst[0]):
            order = DISORDERED

        i += 1;

    return order


def binary_search(lst: list[int | float], value: int | float) -> int:
    l = 0
    r = len(lst) - 1

    while l < r:
        mid = (l + r) // 2

        if (lst[mid] < value):
            l = mid + 1
        else:
            r = mid

    return l


def find_closest_interval(lst: list[int | float], value: int | float, 
                          interval: int) -> int:
    offset = binary_search(lst, value)
    amount = len(lst)
    half = interval // 2
    left = 0

    if (offset - half >= 0):
        left = offset - half

    if (offset + half >= amount):
        left = amount - interval

    return left


def matrix_find_greatest_row(matrix: list[list[int | float]], key) -> int:
    index = 0
    max_value = key(matrix[0])

    for i in range(1, len(matrix)):
        value = key(matrix[i])

        if (max_value < value):
            max_value = value
            index = i

    return index


def solve_linear_system(matrix: list[list[int | float]]) -> list[float]:
    buffer = [i.copy() for i in matrix]

    for i in range(len(buffer)):
        index = matrix_find_greatest_row(buffer[i:], lambda x: abs(x[i]))
        buffer[i], buffer[i + index] = buffer[i + index], buffer[i]

        for j in range(i + 1, len(buffer[i])):
            buffer[i][j] /= buffer[i][i]

        buffer[i][i] = 1

        for k in range(i + 1, len(buffer)):
            for j in range(i + 1, len(buffer[i])):
                buffer[k][j] -= buffer[i][j] * buffer[k][i]

            buffer[k][i] = 0

    out = [0.0] * (len(matrix) - 1) + [buffer[-1][-1]]

    for i in range(len(buffer) - 1, 0, -1):
        for j in range(i, len(buffer)):
            buffer[i - 1][-1] -= buffer[j][-1] * buffer[i - 1][j]
            buffer[i - 1][j] = 0

        out[i - 1] = buffer[i - 1][-1]

    return out


def combinations(n, k):
    return math.factorial(n) / (math.factorial(k) * math.factorial(n - k))

