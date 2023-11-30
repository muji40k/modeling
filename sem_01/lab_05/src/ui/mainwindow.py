from PyQt5 import QtCore, QtWidgets, uic
import matplotlib
matplotlib.use('Qt5Agg')

from dataclasses import dataclass
from typing import Callable

from threading import Thread
import sys

import math

from matplotlib.figure import Figure as MpFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib import cm
import numpy

import src.common_task as common
import src.task as task

from src.ui.init_type import InitTypeWidget, TYPE_BOTTOM, TYPE_TOP, TYPE_LEFT, \
                             TYPE_RIGHT
import out.form as form

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = MpFigure(figsize=(width, height), dpi=dpi)
        self.axes = []
        super(MplCanvas, self).__init__(self.fig)

@dataclass
class InnerResult:
    x : list[float]
    y : list[float]
    temperature : list[list[float]]
    res : list[task.IterResult]

def calc_thread(handle : task.TaskHandle, result : InnerResult, progress : task.Progress) -> None:
    _result = common.solve(handle, progress)
    result.x = _result.x
    result.y = _result.y
    result.temperature = _result.temperature
    result.res.clear()

    for r in _result.res:
        r.__class__ = task.IterResult
        result.res.append(r)

class MainWindow(QtWidgets.QMainWindow):
    _k_F = 0
    _k_T_MAIN = 1
    _k_T_x = 2
    _k_T_z = 3

    _label_x = {_k_F      : "x [см]",
                _k_T_MAIN : "x [см]",
                _k_T_x    : "x [см]",
                _k_T_z    : "z [см]"}

    _label_y = {_k_F      : "z [см]",
                _k_T_MAIN : "z [см]",
                _k_T_x    : "Температура [K]",
                _k_T_z    : "Температура [K]"}

    _label_z = {_k_F      : "Поток [$\\frac{Вт}{см^2}$]",
                _k_T_MAIN : "Температура [K]"}

    _is_3d = {_k_F : True, _k_T_MAIN : True, _k_T_x : False, _k_T_z : False}

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs);

        self.start = False
        self.thread : Thread
        self.result : InnerResult = InnerResult([], [], [], [])
        self.progress : task.Progress = task.Progress()

        # self.ui = uic.loadUi("./ui/form.ui", self)
        self.ui = form.Ui_MainWindow()
        self.ui.setupUi(self)

        self.figure = {}

        self.figure[self._k_F] = MplCanvas(self.ui.tab_graph_F)
        toolbar = NavigationToolbar2QT(self.figure[self._k_F], self.ui.tab_graph_F)
        self.ui.verticalLayout_graph_F.addWidget(toolbar)
        self.ui.verticalLayout_graph_F.addWidget(self.figure[self._k_F])
        self.ui.verticalLayout_graph_F.setStretch(0, 1)
        self.figure[self._k_F].axes.append(self.figure[self._k_F].fig.add_subplot(1, 1, 1, projection="3d"))

        self.figure[self._k_T_MAIN] = MplCanvas(self.ui.tab_graph_T_main)
        toolbar = NavigationToolbar2QT(self.figure[self._k_T_MAIN], self.ui.tab_graph_T_main)
        self.ui.verticalLayout_7.insertWidget(0, toolbar, 0)
        self.ui.verticalLayout_7.insertWidget(1, self.figure[self._k_T_MAIN], 1)
        self.ui.verticalLayout_7.setStretch(2, 0)
        self.figure[self._k_T_MAIN].axes.append(self.figure[self._k_T_MAIN].fig.add_subplot(1, 1, 1, projection="3d"))

        self.figure[self._k_T_x] = MplCanvas(self.ui.tab_graph_T_x)
        toolbar = NavigationToolbar2QT(self.figure[self._k_T_x], self.ui.tab_graph_T_x)
        self.ui.verticalLayout_3.insertWidget(0, toolbar, 0)
        self.ui.verticalLayout_3.insertWidget(1, self.figure[self._k_T_x], 1)
        self.ui.verticalLayout_3.setStretch(2, 0)
        self.figure[self._k_T_x].axes.append(self.figure[self._k_T_x].fig.add_subplot(1, 1, 1))

        self.figure[self._k_T_z] = MplCanvas(self.ui.tab_graph_T_z)
        toolbar = NavigationToolbar2QT(self.figure[self._k_T_z], self.ui.tab_graph_T_z)
        self.ui.verticalLayout_6.insertWidget(0, toolbar, 0)
        self.ui.verticalLayout_6.insertWidget(1, self.figure[self._k_T_z], 1)
        self.ui.verticalLayout_6.setStretch(2, 0)
        self.figure[self._k_T_z].axes.append(self.figure[self._k_T_z].fig.add_subplot(1, 1, 1))

        self.clear_all_axes();

        self.left = InitTypeWidget(TYPE_LEFT, parent=self.ui.tab_left)
        self.right = InitTypeWidget(TYPE_RIGHT, parent=self.ui.tab_right)
        self.top = InitTypeWidget(TYPE_TOP, parent=self.ui.tab_top)
        self.bottom = InitTypeWidget(TYPE_BOTTOM, parent=self.ui.tab_bottom)

        self.ui.verticalLayout.addWidget(self.left)
        self.ui.verticalLayout_8.addWidget(self.right)
        self.ui.verticalLayout_10.addWidget(self.top)
        self.ui.verticalLayout_12.addWidget(self.bottom)

        self.timer = QtCore.QTimer()
        self.timer.start(100)

        self.timer.timeout.connect(self.timeout)
        self.ui.pushButton_calculate.clicked.connect(self.on_calculate_clicked)

        self.ui.doubleSpinBox_x0.valueChanged.connect(self.reset_x_step)
        self.ui.doubleSpinBox_x_max.valueChanged.connect(self.reset_x_step)
        self.ui.spinBox_steps.valueChanged.connect(self.reset_x_step)

        self.ui.doubleSpinBox_z0.valueChanged.connect(self.reset_z_step)
        self.ui.doubleSpinBox_z_max.valueChanged.connect(self.reset_z_step)
        self.ui.spinBox_steps.valueChanged.connect(self.reset_z_step)

        self.ui.horizontalSlider_x.sliderMoved.connect(self.on_z_slider_moved)
        self.ui.horizontalSlider_x.sliderReleased.connect(self.on_z_slider_changed)

        self.ui.horizontalSlider_z.sliderMoved.connect(self.on_x_slider_moved)
        self.ui.horizontalSlider_z.sliderReleased.connect(self.on_x_slider_changed)

        self.ui.doubleSpinBox_f_max.valueChanged.connect(self.on_f_changed)
        self.ui.doubleSpinBox_beta.valueChanged.connect(self.on_f_changed)
        self.ui.doubleSpinBox_x0.valueChanged.connect(self.on_f_changed)
        self.ui.doubleSpinBox_x_max.valueChanged.connect(self.on_f_changed)
        self.ui.doubleSpinBox_x_c.valueChanged.connect(self.on_f_changed)
        self.ui.doubleSpinBox_z0.valueChanged.connect(self.on_f_changed)
        self.ui.doubleSpinBox_z_max.valueChanged.connect(self.on_f_changed)
        self.ui.doubleSpinBox_z_c.valueChanged.connect(self.on_f_changed)
        self.ui.spinBox_steps.valueChanged.connect(self.on_f_changed)

        self.ui.horizontalSlider_x_val.valueChanged.connect(self.on_val_slider_moved)
        self.ui.horizontalSlider_z_val.valueChanged.connect(self.on_val_slider_moved)

        self.reset_x_step()
        self.reset_z_step()
        self.on_f_changed()

    def timeout(self):
        if (self.start):
            m = max([max(map(lambda x, y : abs(x - y),
                             self.progress.current[i],
                             self.progress.prev[i]))
                     for i in range(len(self.progress.current))]) \
                / self.progress.timestep
            self.ui.label_status.setText("dy/dt -> {:0.3g}".format(m))

        if (not self.start or self.thread.is_alive()):
            return

        self.start = False
        self.thread.join()

        self.show_main_graph()
        self.show_x_graph(1)
        self.show_z_graph(1)

        self.on_val_slider_moved()
        self.ui.label_status.setText("Готово")

    def construct_F(self) -> Callable[[float, float], float]:
        f_max = self.ui.doubleSpinBox_f_max.value()
        beta = self.ui.doubleSpinBox_beta.value()
        x = self.ui.doubleSpinBox_x_c.value()
        z = self.ui.doubleSpinBox_z_c.value()

        return task.funcF(f_max, beta, x, z)
        # return task.funcFSmooth(f_max, x, z)

    def construct_lambda(self) -> Callable[[float], float]:
        a = self.ui.doubleSpinBox_a.value() * 10 ** self.ui.spinBox_a.value()
        b = self.ui.doubleSpinBox_b.value() 
        c = self.ui.doubleSpinBox_c.value() * 10 ** self.ui.spinBox_c.value()
        m = self.ui.doubleSpinBox_m.value()

        return task.funcLambda(a, b, c, m)

    def clear_axes(self, fig : int):
        axes = self.figure[fig].axes[0]
        axes.cla()
        axes.grid(True)

        axes.set_xlabel(self._label_x[fig])
        axes.set_ylabel(self._label_y[fig])

        if (self._is_3d[fig]):
            axes.set_zlabel(self._label_z[fig])

    def clear_all_axes(self):
        for fig in self.figure:
            self.clear_axes(fig)

    def show_main_graph(self):
        self.clear_axes(self._k_T_MAIN)

        X, Y = numpy.meshgrid(self.result.x, self.result.y)
        TMP = numpy.array([numpy.array(i) for i in self.result.temperature])

        self.figure[self._k_T_MAIN].axes[0].plot_surface(X, Y, TMP, cmap=cm.coolwarm)
        self.figure[self._k_T_MAIN].draw()

    def show_z_graph(self, pstep):
        a = self.ui.horizontalSlider_x.value() \
            / self.ui.horizontalSlider_x.maximum()
        m, index = math.modf(a * len(self.result.x))
        index = int(index)

        if (len(self.result.temperature[0]) <= index + 1):
            inter_f = lambda i : i[-1]
        else:
            inter_f = lambda i : (1 - m) * i[index] + m * i[index + 1]

        r = (1 - a) * self.ui.doubleSpinBox_z0.value() \
            + a * self.ui.doubleSpinBox_z_max.value()

        self.ui.label_x_val.setText("({:0.3g})".format(r))

        val = [inter_f(i) for i in self.result.temperature[::pstep]]

        self.clear_axes(self._k_T_z)
        self.figure[self._k_T_z].axes[0].plot(self.result.y[::pstep], val)
        self.figure[self._k_T_z].draw()

    def show_x_graph(self, pstep):
        a = self.ui.horizontalSlider_z.value() \
            / self.ui.horizontalSlider_z.maximum()
        m, index = math.modf(a * len(self.result.y))
        index = int(index)

        r = (1 - a) * self.ui.doubleSpinBox_z0.value() \
            + a * self.ui.doubleSpinBox_z_max.value()
        self.ui.label_z_val.setText("({:0.3g})".format(r))

        if (len(self.result.x) - 1 <= index):
            val = self.result.temperature[-1][::pstep]
        else:
            val = list(map(lambda x, y : (1 - m) * x + m * y,
                           self.result.temperature[index][::pstep],
                           self.result.temperature[index + 1][::pstep]))

        self.clear_axes(self._k_T_x)
        self.figure[self._k_T_x].axes[0].plot(self.result.x[::pstep], val)
        self.figure[self._k_T_x].draw()

    def on_calculate_clicked(self):
        if (self.start):
            return

        handle = task.TaskHandle()

        handle.lambda_f = self.construct_lambda()
        handle.f_f = self.construct_F()

        handle.t_0 = self.ui.doubleSpinBox_t0.value()

        handle.bottom = self.bottom.getInitialValue()
        handle.top    = self.top.getInitialValue()
        handle.left   = self.left.getInitialValue()
        handle.right  = self.right.getInitialValue()

        handle.x_0 = self.ui.doubleSpinBox_x0.value()
        handle.x_max = self.ui.doubleSpinBox_x_max.value()
        handle.z_0 = self.ui.doubleSpinBox_z0.value()
        handle.z_max = self.ui.doubleSpinBox_z_max.value()

        handle.x_steps = self.ui.spinBox_steps.value()
        handle.z_steps = self.ui.spinBox_steps.value()

        handle.timestep = self.ui.doubleSpinBox_t_step.value()

        handle.eps_lin = 10 ** self.ui.spinBox_eps_lin.value()
        handle.eps_time = 10 ** self.ui.spinBox_eps_time.value()

        self.start = True
        self.thread = Thread(target=calc_thread, args=(handle, self.result, self.progress))
        self.thread.daemon = True
        self.thread.start()


    def reset_x_step(self):
        self.ui.label_x_step.setText("Шаг (x): {:0.6g}"
                                   .format((self.ui.doubleSpinBox_x_max.value() - self.ui.doubleSpinBox_x0.value()) / self.ui.spinBox_steps.value()))

    def reset_z_step(self):
        self.ui.label_z_step.setText("Шаг (z): {:0.6g}"
                                   .format((self.ui.doubleSpinBox_z_max.value() - self.ui.doubleSpinBox_z0.value()) / self.ui.spinBox_steps.value()))

    def on_x_slider_moved(self):
        self.show_x_graph(2)

    def on_x_slider_changed(self):
        self.show_x_graph(1)

    def on_z_slider_moved(self):
        self.show_z_graph(2)

    def on_z_slider_changed(self):
        self.show_z_graph(1)

    def on_f_changed(self):
        x0 = self.ui.doubleSpinBox_x0.value()
        x_max = self.ui.doubleSpinBox_x_max.value()
        x_num = self.ui.spinBox_steps.value()
        z0 = self.ui.doubleSpinBox_z0.value()
        z_max = self.ui.doubleSpinBox_z_max.value()
        z_num = self.ui.spinBox_steps.value()

        if (not x_num or not z_num):
            return

        f = self.construct_F()

        X = numpy.linspace(x0, x_max, x_num)
        Y = numpy.linspace(z0, z_max, z_num)

        TMP = numpy.array([numpy.array([f(i, j) for i in X]) for j in Y])
        X, Y = numpy.meshgrid(X, Y)

        self.clear_axes(self._k_F)
        self.figure[self._k_F].axes[0].plot_surface(X, Y, TMP, cmap=cm.coolwarm)
        self.figure[self._k_F].draw()

    def on_val_slider_moved(self):
        x0 = self.ui.doubleSpinBox_x0.value()
        x_max = self.ui.doubleSpinBox_x_max.value()
        z0 = self.ui.doubleSpinBox_z0.value()
        z_max = self.ui.doubleSpinBox_z_max.value()

        x_frac = self.ui.horizontalSlider_x_val.value() \
                 / self.ui.horizontalSlider_x_val.maximum()
        z_frac = self.ui.horizontalSlider_z_val.value() \
                 / self.ui.horizontalSlider_z_val.maximum()

        x_r, x_index = math.modf(x_frac * len(self.result.x))
        z_r, z_index = math.modf(z_frac * len(self.result.y))
        x_index = int(x_index)
        z_index = int(z_index)
        val = 0

        if (len(self.result.x) <= x_index + 1 and len(self.result.y) <= z_index + 1):
            val = self.result.temperature[-1][-1]
        elif (len(self.result.x) <= x_index + 1):
            val = (1 - z_r) * self.result.temperature[z_index][-1] \
                  + z_r * self.result.temperature[z_index + 1][-1]
        elif (len(self.result.y) <= z_index + 1):
            val = (1 - x_r) * self.result.temperature[-1][x_index] \
                  + x_r * self.result.temperature[-1][x_index + 1]
        else:
            tmp = list(map(lambda x, y : (1 - z_r) * x + z_r * y,
                           self.result.temperature[z_index][x_index : x_index + 2],
                           self.result.temperature[z_index + 1][x_index : x_index + 2]))
            val = (1 - x_r) * tmp[0] + x_r * tmp[1]

        self.ui.label_x.setText("x: ({:0.3g})".format(x0 + x_frac * (x_max - x0)))
        self.ui.label_z.setText("z: ({:0.3g})".format(z0 + z_frac * (z_max - z0)))
        self.ui.label_T.setText("T: ({:0.3f})".format(val))

