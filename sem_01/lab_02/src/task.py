#! /bin/python
from dataclasses import dataclass
import sys
from abc import ABC, abstractmethod

import math

from src.runge_kutta import runge_kutta
from src.interpolate import linear_interpolation

@dataclass
class TaskHandle:
    current_temperature_table : dict[float, float]
    current_m_table : dict[float, float]
    temperature_sigma_table : dict[float, float]

    method : int = 0
    steps : int = 0
    beta : float = 0

    radius : float = 0
    length : float = 0
    inductance : float = 0
    capacity : float = 0
    resistance : float = 0
    voltage : float = 0
    current : float = 0
    temperature : float = 0

    resistance_mode : bool = False


@dataclass
class TaskResult:
    timing : list[float]
    current : list[float]
    voltage : list[float]
    voltage_add : list[float]
    resistance : list[float]
    temperature : list[float]


class funcT:
    def __init__(self, handle : TaskHandle):
        self.handle = handle
        self.current_temp = sorted(list(handle.current_temperature_table.keys()))
        self.temperature = [handle.current_temperature_table[i] for i in self.current_temp]
        self.current_m = sorted(list(handle.current_m_table.keys()))
        self.m = [handle.current_m_table[i] for i in self.current_m]

    def __call__(self, current : float, z : float) -> float:
        t0 = linear_interpolation(current, self.current_temp, self.temperature)
        m = linear_interpolation(current, self.current_m, self.m)
        return t0 + (self.handle.temperature - t0) * z ** m


class funcSigma:
    def __init__(self, handle : TaskHandle):
        self.t = funcT(handle)
        self.handle = handle
        self.current = 0
        self.temp_sigma = sorted(list(handle.temperature_sigma_table.keys()))
        self.sigma = [handle.temperature_sigma_table[i] for i in self.temp_sigma]

    def setCurrent(self, current : float) -> None:
        self.current = current

    def __call__(self, z : float, _ : list[float]) -> float:
        t = self.t(self.current, z)
        return linear_interpolation(t, self.temp_sigma, self.sigma) * z


class funcResistance(ABC):
    @abstractmethod
    def __call__(self, current : float) -> float:
        pass

class funcResistanceMain(funcResistance):
    def __init__(self, handle : TaskHandle):
        self.sigma = funcSigma(handle)
        self.handle = handle
        self.current = 0
        self.sigma.setCurrent(0)
        self.sigma_val = runge_kutta(self.handle.method, self.handle.steps,
                                     1, 0, [0], self.sigma, beta=self.handle.beta)[0]

    def __call__(self, current : float) -> float:
        if (sys.float_info.epsilon < abs(current - self.current)):
            self.sigma.setCurrent(current)
            self.sigma_val = runge_kutta(self.handle.method, self.handle.steps,
                                         1, 0, [0], self.sigma,
                                         beta=self.handle.beta)[0]

        return self.handle.length \
               / (2 * math.pi * self.handle.radius ** 2 * self.sigma_val)

class funcResistancePlain(funcResistance):
    def __init__(self, handle : TaskHandle):
        self.handle = handle

    def __call__(self, _ : float) -> float:
        return -self.handle.resistance


class funcI:
    def __init__(self, handle : TaskHandle, resistance : funcResistance):
        self.handle = handle
        self.resistance = resistance

    def __call__(self, _ : float, ui : list[float]) -> float:
        return (ui[0]
                - (self.handle.resistance + self.resistance(ui[1])) * ui[1]) \
               / self.handle.inductance


class funcU:
    def __init__(self, handle : TaskHandle):
        self.handle = handle

    def __call__(self, _ : float, ui : list[float]) -> float:
        return - ui[1] / self.handle.capacity


def solve(start_time : float, stop_time : float, steps : int, handle : TaskHandle) -> TaskResult:
    out = TaskResult([], [], [], [], [], [])

    if (stop_time < start_time):
        start_time, stop_time = stop_time, start_time

    if (handle.resistance_mode):
        resistance = funcResistancePlain(handle)
    else:
        resistance = funcResistanceMain(handle)

    voltage = funcU(handle)
    current = funcI(handle, resistance)

    h = (stop_time - start_time) / (steps - 1)
    out.timing = [start_time + i * h for i in range(steps)]

    for i in range(steps):
        t = start_time + i * h
        res_ui = runge_kutta(handle.method, handle.steps, t, start_time,
                             [handle.voltage, handle.current], voltage,
                             current, beta=handle.beta)
        out.voltage.append(res_ui[0])
        out.current.append(res_ui[1])

    current_temp = sorted(list(handle.current_temperature_table.keys()))
    temperature = [handle.current_temperature_table[i] for i in current_temp]

    for i in out.current:
        r = resistance(i)
        out.resistance.append(r)
        out.voltage_add.append(i * r)
        out.temperature.append(linear_interpolation(i, current_temp, temperature))

    return out

