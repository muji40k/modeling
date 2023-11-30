from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QTableWidget
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.figure import Figure as MpFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pylab as pl

import csv
from threading import Thread
import sys

from dataclasses import dataclass
from typing import Callable
import math

import out.form as form

from src.common_task import solve
from src.task import TaskHandle, IterResult, funcF, funcFConst, funcC, Progress
from misc.interpolate import TableFunc

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = MpFigure(figsize=(width, height), dpi=dpi)
        self.axes = []
        super(MplCanvas, self).__init__(self.fig)

@dataclass
class InnerResult:
    radius : list[float]
    timeline : list[float]
    temperature : list[list[float]]
    res : list[IterResult]

def calc_thread(handle : TaskHandle, result : InnerResult, progress : Progress) -> None:
    _result = solve(handle, progress)
    result.radius = _result.radius
    result.timeline = _result.timeline
    result.temperature = _result.temperature
    result.res.clear()

    for r in _result.res:
        r.__class__ = IterResult
        result.res.append(r)

class MainWindow(QtWidgets.QMainWindow):
    _k_F = 0
    _k_T_MAIN = 1
    _k_T_t = 2
    _k_T_r = 3

    _label_x = {_k_F      : "Время [мкс]",
                _k_T_MAIN : "Радиус [см]",
                _k_T_t    : "Время [мкс]",
                _k_T_r    : "Радиус [см]"}

    _label_y = {_k_F      : "Поток [$\\frac{Вт}{см^2}$]",
                _k_T_MAIN : "Температура [K]",
                _k_T_t    : "Температура [K]",
                _k_T_r    : "Температура [K]"}

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs);

        self.start = False
        self.thread : Thread
        self.result : InnerResult = InnerResult([], [], [], [])

        # self.ui = uic.loadUi("./ui/form.ui", self)
        self.ui = form.Ui_MainWindow()
        self.ui.setupUi(self)

        self.figure = {}

        self.figure[self._k_F] = MplCanvas(self.ui.tab_graph_F)
        toolbar = NavigationToolbar2QT(self.figure[self._k_F], self.ui.tab_graph_F)
        self.ui.verticalLayout_graph_F.addWidget(toolbar)
        self.ui.verticalLayout_graph_F.addWidget(self.figure[self._k_F])
        self.ui.verticalLayout_graph_F.setStretch(0, 1)
        self.figure[self._k_F].axes.append(self.figure[self._k_F].fig.add_subplot(1, 1, 1))

        self.figure[self._k_T_MAIN] = MplCanvas(self.ui.tab_graph_T_main)
        toolbar = NavigationToolbar2QT(self.figure[self._k_T_MAIN], self.ui.tab_graph_T_main)
        self.ui.verticalLayout_graph_T_main.addWidget(toolbar)
        self.ui.verticalLayout_graph_T_main.addWidget(self.figure[self._k_T_MAIN])
        self.ui.verticalLayout_graph_T_main.setStretch(0, 1)
        self.figure[self._k_T_MAIN].axes.append(self.figure[self._k_T_MAIN].fig.add_subplot(1, 1, 1))

        self.figure[self._k_T_t] = MplCanvas(self.ui.tab_graph_T_time)
        toolbar = NavigationToolbar2QT(self.figure[self._k_T_t], self.ui.tab_graph_T_time)
        self.ui.verticalLayout_3.insertWidget(0, toolbar, 0)
        self.ui.verticalLayout_3.insertWidget(1, self.figure[self._k_T_t], 1)
        self.ui.verticalLayout_3.setStretch(2, 0)
        self.figure[self._k_T_t].axes.append(self.figure[self._k_T_t].fig.add_subplot(1, 1, 1))

        self.figure[self._k_T_r] = MplCanvas(self.ui.tab_graph_T_pos)
        toolbar = NavigationToolbar2QT(self.figure[self._k_T_r], self.ui.tab_graph_T_pos)
        self.ui.verticalLayout_6.insertWidget(0, toolbar, 0)
        self.ui.verticalLayout_6.insertWidget(1, self.figure[self._k_T_r], 1)
        self.ui.verticalLayout_6.setStretch(2, 0)
        self.figure[self._k_T_r].axes.append(self.figure[self._k_T_r].fig.add_subplot(1, 1, 1))

        sm = pl.cm.ScalarMappable(norm=pl.Normalize(vmin = 0, vmax=self.ui.doubleSpinBox_t_end.value()), cmap="rainbow")
        self.colorbar = self.figure[self._k_T_MAIN].fig.colorbar(sm, ax=self.figure[self._k_T_MAIN].axes[0])

        self.loadTable(self.ui.tableWidget_lambda, "res/lambda.csv")
        self.loadTable(self.ui.tableWidget_k, "res/k.csv")

        self.clear_all_axes();

        self.timer = QtCore.QTimer()
        self.timer.start(100)

        self.timer.timeout.connect(self.timeout)
        self.ui.pushButton_calculate.clicked.connect(self.on_calculate_clicked)
        self.ui.pushButton_load_lambda.clicked.connect(self.on_load_lambda_clicked)
        self.ui.pushButton_load_k.clicked.connect(self.on_load_k_clicked)

        self.ui.doubleSpinBox_r0.valueChanged.connect(self.reset_step)
        self.ui.doubleSpinBox_r_max.valueChanged.connect(self.reset_step)
        self.ui.spinBox_steps.valueChanged.connect(self.reset_step)

        self.ui.doubleSpinBox_t_end.valueChanged.connect(self.reset_step_time)
        self.ui.spinBox_steps_time.valueChanged.connect(self.reset_step_time)

        self.ui.horizontalSlider_r.sliderMoved.connect(self.on_r_slider_moved)
        self.ui.horizontalSlider_r.sliderReleased.connect(self.on_r_slider_changed)

        self.ui.horizontalSlider_t.sliderMoved.connect(self.on_t_slider_moved)
        self.ui.horizontalSlider_t.sliderReleased.connect(self.on_t_slider_changed)

        self.ui.doubleSpinBox_t_end.valueChanged.connect(self.on_impulse_changed)
        self.ui.doubleSpinBox_f_max.valueChanged.connect(self.on_impulse_changed)
        self.ui.doubleSpinBox_t_max.valueChanged.connect(self.on_impulse_changed)
        self.ui.doubleSpinBox_v.valueChanged.connect(self.on_impulse_changed)
        self.ui.checkBox_f_const.stateChanged.connect(self.on_impulse_changed)

        self.reset_step()
        self.reset_step_time()
        self.show_func(self._k_F, 100, self.construct_F())


    def timeout(self):
        if (self.start):
            self.ui.progressBar.setValue(int(100 * self.progress.get()))

        if (not self.start or self.thread.is_alive()):
            return

        self.start = False
        self.thread.join()

        self.show_main_graph()
        self.show_t_graph(1)
        self.show_r_graph(1)

        if (self.ui.checkBox_f_const.isChecked()):
            iter = self.result.res[-1]
            print("f1: {:0.6g}\nf2: {:0.6g}".format(iter.f1, iter.f2))

    def construct_F(self) -> Callable[[float], float]:
        # return lambda x : x * 200 if x < 0.5 else 0
        # return lambda x : x / 5 if x < 500 else 0
        f_max = self.ui.doubleSpinBox_f_max.value()
        t_max = self.ui.doubleSpinBox_t_max.value()
        v = self.ui.doubleSpinBox_v.value()

        if (self.ui.checkBox_f_const.isChecked()):
            return funcFConst(f_max)

        return funcF(f_max, t_max, v)

    def construct_C(self) -> Callable[[float], float]:
        a = self.ui.doubleSpinBox_a_2.value()
        b = self.ui.doubleSpinBox_b_2.value() * 10 ** self.ui.spinBox_b_2_eps.value()
        c = self.ui.doubleSpinBox_c_2.value() * 10 ** self.ui.spinBox_c_2_eps.value()
        m = self.ui.doubleSpinBox_m_2.value()

        return funcC(a, b, c, m)

    def clear_axes(self, fig : int):
        axes = self.figure[fig].axes[0]
        axes.cla()
        axes.grid(True)
        axes.set_xlabel(self._label_x[fig])
        axes.set_ylabel(self._label_y[fig])

    def clear_all_axes(self):
        for fig in self.figure:
            self.clear_axes(fig)

    def show_func(self, fig : int, steps : int, func : Callable[[float], float]) -> None:
        s = 0
        e = self.ui.doubleSpinBox_t_end.value()
        step = (e - s) / steps

        grid = [s + i * step for i in range(steps + 1)]
        val = [func(i / 1000) for i in grid]
        # val = [func(i) for i in grid]

        self.clear_axes(fig)
        self.figure[fig].axes[0].plot(grid, val)
        self.figure[fig].draw()

    def show_main_graph(self):
        self.clear_axes(self._k_T_MAIN)

        n = len(self.result.temperature)
        i_n = 1 / n
        colors = pl.cm.rainbow([i * i_n for i in range(n)])

        for i, temp in enumerate(self.result.temperature):
            self.figure[self._k_T_MAIN].axes[0].plot(self.result.radius, temp, color=colors[i])

        sm = pl.cm.ScalarMappable(norm=pl.Normalize(vmin = 0, vmax=self.result.timeline[-1]), cmap="rainbow")
        self.colorbar.update_normal(sm)

        self.figure[self._k_T_MAIN].draw()

    def show_t_graph(self, pstep):
        a = self.ui.horizontalSlider_r.value() \
            / self.ui.horizontalSlider_r.maximum()
        m, index = math.modf(a * len(self.result.radius))
        index = int(index)

        if (len(self.result.temperature[0]) <= index + 1):
            inter_f = lambda i : i[-1]
        else:
            inter_f = lambda i : (1 - m) * i[index] + m * i[index + 1]

        r = (1 - a) * self.ui.doubleSpinBox_r0.value() \
            + a * self.ui.doubleSpinBox_r_max.value()

        self.ui.label_r_val.setText("({:0.3g})".format(r))

        timeline = [i for i in self.result.timeline[::pstep]]
        val = [inter_f(i) for i in self.result.temperature[::pstep]]

        self.clear_axes(self._k_T_t)
        self.figure[self._k_T_t].axes[0].plot(timeline, val)
        self.figure[self._k_T_t].draw()

    def show_r_graph(self, pstep):
        a = self.ui.horizontalSlider_t.value() \
            / self.ui.horizontalSlider_t.maximum()
        m, index = math.modf(a * len(self.result.timeline))
        index = int(index)

        t = a * self.ui.doubleSpinBox_t_end.value()
        self.ui.label_t_val.setText("({:0.3g})".format(t))

        radius = [i for i in self.result.radius[::pstep]]

        if (len(self.result.timeline) - 1 <= index):
            val = self.result.temperature[-1][::pstep]
        else:
            val = list(map(lambda x, y : (1 - m) * x + m * y,
                           self.result.temperature[index][::pstep],
                           self.result.temperature[index + 1][::pstep]))

        self.clear_axes(self._k_T_r)
        self.figure[self._k_T_r].axes[0].plot(radius, val)
        self.figure[self._k_T_r].draw()

    def on_calculate_clicked(self):
        if (self.start):
            return

        lambda_t = self.getTable(self.ui.tableWidget_lambda)
        k_t = self.getTable(self.ui.tableWidget_k)

        lambda_t_list = sorted(list(lambda_t.keys()))
        lambda_list = [lambda_t[i] for i in lambda_t_list]

        k_t_list = sorted(list(k_t.keys()))
        k_list = [k_t[i] for i in k_t_list]

        handle = TaskHandle()

        handle.lambda_f = TableFunc(lambda_t_list, lambda_list)
        handle.k_f = TableFunc(k_t_list, k_list)
        handle.c_f = self.construct_C()
        handle.f_f = self.construct_F()

        handle.n = self.ui.doubleSpinBox_n.value()
        handle.t0 = self.ui.doubleSpinBox_t0.value()
        handle.alpha = self.ui.doubleSpinBox_alpha.value()

        handle.r0 = self.ui.doubleSpinBox_r0.value()
        handle.r_max = self.ui.doubleSpinBox_r_max.value()
        handle.steps = self.ui.spinBox_steps.value()

        handle.time_start = 0
        handle.time_end = self.ui.doubleSpinBox_t_end.value()
        handle.time_steps = self.ui.spinBox_steps_time.value()

        handle.eps = 10 ** self.ui.spinBox_eps1.value()

        self.start = True
        self.progress = Progress(handle)
        self.thread = Thread(target=calc_thread, args=(handle, self.result, self.progress))
        self.thread.daemon = True
        self.thread.start()


    def getTable(self, table : QTableWidget) -> dict[float, float]:
        out : dict[float, float] = {}

        for i in range(table.rowCount()):
            out[float(table.item(i, 0).text())] = float(table.item(i, 1).text())

        return out

    def loadTable(self, table : QTableWidget, filename : str):
        table.clear()

        with open(filename, "r") as file:
            spamreader = csv.reader(file, delimiter=',')
            i = 0

            for row in spamreader:
                if (0 == i):
                    table.setHorizontalHeaderLabels(row)
                else:
                    table.insertRow(i - 1)
                    table.setItem(i - 1 , 0, QTableWidgetItem(row[0]))
                    table.setItem(i - 1 , 1, QTableWidgetItem(row[1]))

                i += 1

    def on_load_lambda_clicked(self):
        filename = QFileDialog.getOpenFileName(None, "Open file", "./", "Image (*.csv)")[0]

        if ("" != filename):
            self.loadTable(self.ui.tableWidget_lambda, filename)

    def on_load_k_clicked(self):
        filename = QFileDialog.getOpenFileName(None, "Open file", "./", "Image (*.csv)")[0]

        if ("" != filename):
            self.loadTable(self.ui.tableWidget_k, filename)

    def reset_step(self):
        self.ui.label_step.setText("Шаг (r): {:0.6g}"
                                   .format((self.ui.doubleSpinBox_r_max.value() - self.ui.doubleSpinBox_r0.value()) / self.ui.spinBox_steps.value()))

    def reset_step_time(self):
        self.ui.label_step_time.setText("Шаг (t): {:0.6g}"
                                        .format(self.ui.doubleSpinBox_t_end.value() / self.ui.spinBox_steps_time.value()))

    def on_r_slider_moved(self):
        self.show_t_graph(2)

    def on_r_slider_changed(self):
        self.show_t_graph(1)

    def on_t_slider_moved(self):
        self.show_r_graph(2)

    def on_t_slider_changed(self):
        self.show_r_graph(1)

    def on_impulse_changed(self):
        if (sys.float_info.epsilon > abs(self.ui.doubleSpinBox_v.value())):
            return

        if (sys.float_info.epsilon > abs(self.ui.doubleSpinBox_t_max.value())):
            return

        self.show_func(self._k_F, 1000, self.construct_F())

