#! /bin/python
from typing import Callable
from dataclasses import dataclass
import sys
import cli as cl
import prettytable

from picard_polinomial import PicardFuncs
import euler
import picard
import task1
import task2
import task3

def blank_direct(x : float) -> float:
    return x

@dataclass
class TaskData:
    name : str
    exp : str
    x_var : str
    y_var : str
    x_start : float
    y_start : float
    has_direct : bool
    direct_f : Callable[[float], float]
    euler_f : Callable[[float, float], float]
    euler_implicit_f : Callable[[float, float, float], euler.ImplicitEulerResult]
    picard_f : PicardFuncs

@dataclass
class ActiveTask:
    data : TaskData


class TaskPrompt(cl.Prompt):
    def __init__(self, active : ActiveTask):
        self._active = active

    def draw(self) -> None:
        print("\033[01m[{}] $ \033[00m".format(self._active.data.name), end="")


tasks : list[TaskData] = [
    TaskData("task1", "(u^2 + x)u' = 1", "u", "x", 0, 1, True, task1.x,
             task1.dxdy, task1.x_next, PicardFuncs(0, 1, 1, task1.dxdy)),
    TaskData("task2", "1 - 2xuu' = u^3 u'", "u", "x", 0, 0.5, True, task2.x,
             task2.dxdy, task2.x_next, PicardFuncs(0, 0.5, 1, task2.dxdy)),
    TaskData("task3", "u' = x^2 + u^2", "x", "u", 0, 0, False, blank_direct,
             task3.dydx, task3.y_next(-1), PicardFuncs(0, 0, 1, task3.dydx))
]

def rng(start : float, end : float, step : float) -> list[float]:
    out = []
    i = start
    func = lambda sx, ex : sx < ex;

    if (end < start):
        if (0 < step):
            step *= -1

        func = lambda sx, ex : sx > ex

    while (func(i, end)):
        out.append(i)
        i += step

    if (not out):
        return out

    if (sys.float_info.epsilon < abs(out[-1] - end)):
        out.append(end)

    return out


def choose_task(args : list[str], task : ActiveTask) -> int:
    if (len(args) != 2):
        print("Неверное использование: {} task<n>".format(args[0]))
        return 0

    for item in tasks:
        if (item.name == args[1]):
            task.data = item
            return 0

    print("Указанное задание не найдено")

    return 0

def info(_ : list[str], task : ActiveTask) -> int:
    print("Выражение: {}\nНачальные условия: {}({}) = {}\n" .format(task.data.exp,
                                                                    task.data.y_var,
                                                                    task.data.x_start,
                                                                    task.data.y_start))
    return 0


def calculate_direct(args : list[str], task : ActiveTask) -> int:
    if (len(args) != 2):
        print("Неверное использование: {} <{}>".format(args[0], task.data.x_var))
        return 0

    if (not task.data.has_direct):
        print("Для данного задания невозможно получить аналитическое решение")
        return 0

    try:
        x = float(args[1])
    except ValueError:
        print("Значение аргумета {} - вещественное число".format(task.data.x_var))
        return 0

    print("{}({}) = {}".format(task.data.y_var, x, task.data.direct_f(x)))

    return 0;


def euler_explicit(args : list[str], task : ActiveTask) -> int:
    if (len(args) != 3):
        print("Неверное использование: {} <{}> <step>".format(args[0], task.data.x_var))
        return 0

    try:
        x = float(args[1])
    except ValueError:
        print("Значение аргумета {} - вещественное число".format(task.data.x_var))
        return 0

    try:
        h = float(args[2])
    except ValueError:
        print("Значение шага - вещественное число")
        return 0

    x_list = rng(task.data.x_start, x, h)

    print("{}({}) = {}".format(task.data.y_var,
                               x,
                               euler.evaluate_euler(task.data.y_start,
                                                    x_list,
                                                    task.data.euler_f)))

    return 0;


def euler_implicit(args : list[str], task : ActiveTask) -> int:
    if (len(args) != 3):
        print("Неверное использование: {} <{}> <step>".format(args[0], task.data.x_var))
        return 0

    try:
        x = float(args[1])
    except ValueError:
        print("Значение аргумета {} - вещественное число".format(task.data.x_var))
        return 0

    try:
        h = float(args[2])
    except ValueError:
        print("Значение шага - вещественное число")
        return 0

    x_list = rng(task.data.x_start, x, h)

    res = euler.evaluate_implicit_euler(task.data.y_start, x_list,
                                        task.data.euler_implicit_f);

    if (not res.valid):
        print("Не удалось вычислить значение")
    else:
        print("{}({}) = {}".format(task.data.y_var, x, res.value))

    return 0;


def picard_f(args : list[str], task : ActiveTask) -> int:
    if (len(args) != 3):
        print("Неверное использование: {} <{}> <n>".format(args[0], task.data.x_var))
        return 0

    try:
        x = float(args[1])
    except ValueError:
        print("Значение аргумета {} - вещественное число".format(task.data.x_var))
        return 0

    try:
        n = int(args[2])
    except ValueError:
        print("Значение приближения - целое число")
        return 0

    task.data.picard_f.n = n

    print("{}({}) = {}".format(task.data.y_var,
                               x,
                               picard.evaluate_picard(task.data.x_start,
                                                      task.data.y_start,
                                                      x,
                                                      task.data.picard_f)))

    return 0

def picard_show(args : list[str], task : ActiveTask) -> int:
    if (len(args) != 2):
        print("Неверное использование: {} <n>".format(args[0], task.data.x_var))
        return 0

    try:
        n = int(args[1])
    except ValueError:
        print("Значение приближения - целое число")
        return 0

    task.data.picard_f.n = n
    print(task.data.picard_f)

    return 0

def table(args : list[str], task : ActiveTask) -> int:
    if (len(args) != 5):
        print("Неверное использование: {} start_{} end_{} step_{} d{}".format(args[0], task.data.x_var, task.data.x_var, task.data.x_var, task.data.x_var))
        return 0

    try:
        sx = float(args[1])
        ex = float(args[2])
        step = float(args[3])
        dx = float(args[4])
    except ValueError:
        print("Значение аргумента - вещественное число")
        return 0

    values = [[] for i in range(7)]
    x_values = rng(sx, ex, step)

    for i in x_values:
        if (task.data.has_direct):
            values[0].append(task.data.direct_f(i))
        else:
            values[0].append("-")

    for i in x_values:
        x_list = rng(task.data.x_start, i, dx)
        values[1].append(euler.evaluate_euler(task.data.y_start,
                                              x_list,
                                              task.data.euler_f))
        res = euler.evaluate_implicit_euler(task.data.y_start, x_list,
                                            task.data.euler_implicit_f)

        if (not res.valid):
            values[2].append("-")
        else:
            values[2].append(res.value)

    for i in x_values:
        for j in range(4):
            task.data.picard_f.n = j + 1
            values[3 + j].append(picard.evaluate_picard(task.data.x_start,
                                                        task.data.y_start,
                                                        i,
                                                        task.data.picard_f))

    table = prettytable.PrettyTable()

    table.field_names = ["Аргумент", "Аналитическое", "Эйлер (явный)",
                         "Эйлер (неявный)", "Пикар 1", "Пикар 2",
                         "Пикар 3", "Пикар 4"]

    for i in range(len(x_values)):
        table.add_row(["{:0.6g}".format(x_values[i])] + [values[j][i] for j in range(7)])

    print(table)

    return 0



def main() -> int:
    data = ActiveTask(tasks[0]);
    cli = cl.Cli("Лабораторная работа №1", TaskPrompt(data))

    cli.add("choose", "Выбор задания", choose_task, data)
    cli.add("info", "Вывод информации о задании", info, data)
    cli.add("analit", "Найти аналитическое решение в точке", calculate_direct, data)
    cli.add("euler", "Найти решение методом Эйлера в заданной точке с указанным шагом", euler_explicit, data)
    cli.add("euler_implicit", "Найти решение методом Эйлера в заданной точке с указанным шагом", euler_implicit, data)
    cli.add("picard", "Найти решение методом Пикара в заданной точке для указанного приближения", picard_f, data)
    cli.add("picard_show", "Показать значение функции для n-ого приближения в методе Пикара", picard_show, data)
    cli.add("table", "Построить таблицу", table, data)

    return cli.mainloop();


if __name__ == "__main__":
    exit(main());

