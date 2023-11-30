from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QTableWidget
import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
from matplotlib.figure import Figure as MpFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

import csv
from threading import Thread

import out.form as form

from src.task import solve, TaskHandle, TaskResult

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = MpFigure(figsize=(width, height), dpi=dpi)
        self.axes = []
        super(MplCanvas, self).__init__(self.fig)


def calc_thread(handle : TaskHandle, result : TaskResult, start : float, end : float, steps : int) -> None:
    _result = solve(start * 1e-6, end * 1e-6, steps, handle)
    result.current = _result.current
    result.resistance = _result.resistance
    result.temperature = _result.temperature
    result.timing = _result.timing
    result.voltage = _result.voltage
    result.voltage_add = _result.voltage_add


class MainWindow(QtWidgets.QMainWindow):
    _ylabels = ["$I(t) [А]$", "$U(t)$ [В]", "$R_p(t) [Ом]$", "$I(t) R_p(t)$ [В]", "$T_0(t)$ [К]"]

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs);
        self.start = False
        self.thread : Thread
        self.result : TaskResult = TaskResult([], [], [], [], [], [])

        self.ui = form.Ui_MainWindow()
        self.ui.setupUi(self)

        self.figure = MplCanvas(self.ui.frame_plot)
        self.toolbar = NavigationToolbar2QT(self.figure, self.ui.frame_plot)
        self.ui.verticalLayout_plot.addWidget(self.toolbar)
        self.ui.verticalLayout_plot.addWidget(self.figure)
        self.ui.verticalLayout_plot.setStretch(0, 1)

        self.figure.axes.append(self.figure.fig.add_subplot(2, 3, 1))
        self.figure.axes.append(self.figure.fig.add_subplot(2, 3, 2))
        self.figure.axes.append(self.figure.fig.add_subplot(2, 3, 3))
        self.figure.axes.append(self.figure.fig.add_subplot(2, 3, 4))
        self.figure.axes.append(self.figure.fig.add_subplot(2, 3, 6))

        self.loadTable(self.ui.tableWidget_m, "res/m.csv")
        self.loadTable(self.ui.tableWidget_t, "res/t.csv")
        self.loadTable(self.ui.tableWidget_sigma, "res/sigma.csv")

        self.clear_axes();

        self.timer = QtCore.QTimer()
        self.timer.start(100)

        self.timer.timeout.connect(self.timeout)
        self.ui.pushButton_calculate.clicked.connect(self.on_calculate_clicked)
        self.ui.pushButton_load_m.clicked.connect(self.on_load_m_clicked)
        self.ui.pushButton_load_t.clicked.connect(self.on_load_t_clicked)
        self.ui.pushButton_load_sigma.clicked.connect(self.on_load_sigma_clicked)


    def timeout(self):
        if (not self.start or self.thread.is_alive()):
            return

        self.start = False
        self.thread.join()

        for i in range(len(self.result.timing)):
            self.result.timing[i] *= 1e6

        self.clear_axes()
        self.figure.axes[0].plot(self.result.timing, self.result.current)
        self.figure.axes[1].plot(self.result.timing, self.result.voltage)
        self.figure.axes[2].plot(self.result.timing, self.result.resistance)
        self.figure.axes[3].plot(self.result.timing, self.result.voltage_add)
        self.figure.axes[4].plot(self.result.timing, self.result.temperature)

        self.figure.draw()


    def clear_axes(self):
        self.figure.figure.tight_layout(pad=0.5)

        for i, axes in enumerate(self.figure.axes):
            axes.cla()
            axes.grid(True)
            axes.set_xlabel("Время [мкс]")
            axes.set_ylabel(self._ylabels[i])


    def on_calculate_clicked(self):
        if (self.start):
            return

        handle = TaskHandle({}, {}, {})

        handle.radius = self.ui.doubleSpinBox_r.value()
        handle.length = self.ui.doubleSpinBox_l.value()
        handle.inductance = self.ui.doubleSpinBox_L.value() * 10 ** self.ui.spinBox_L_exp.value()
        handle.capacity = self.ui.doubleSpinBox_C.value() * 10 ** self.ui.spinBox_C_exp.value()
        handle.resistance = self.ui.doubleSpinBox_R.value()
        handle.voltage = self.ui.doubleSpinBox_u.value()
        handle.current = self.ui.doubleSpinBox_I.value()
        handle.temperature = self.ui.doubleSpinBox_T.value()

        method = self.ui.comboBox_method.currentIndex()

        if (0 == method):
            handle.method = 1
        elif (1 == method):
            handle.method = 2
            handle.beta = self.ui.doubleSpinBox_beta.value()
        elif (2 == method):
            handle.method = 4

        handle.steps = self.ui.spinBox_steps.value()

        handle.current_m_table = self.getTable(self.ui.tableWidget_m)
        handle.current_temperature_table = self.getTable(self.ui.tableWidget_t)
        handle.temperature_sigma_table = self.getTable(self.ui.tableWidget_sigma)

        handle.resistance_mode = self.ui.checkBox_resistance.isChecked()

        self.start = True
        self.thread = Thread(target=calc_thread, args=(handle, self.result, 
                                                       self.ui.doubleSpinBox_start.value(),
                                                       self.ui.doubleSpinBox_stop.value(),
                                                       self.ui.spinBox_steps_time.value()))
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

    def on_load_m_clicked(self):
        filename = QFileDialog.getOpenFileName(None, "Open file", "./", "Image (*.csv)")[0]

        if ("" != filename):
            self.loadTable(self.ui.tableWidget_m, filename)

    def on_load_t_clicked(self):
        filename = QFileDialog.getOpenFileName(None, "Open file", "./", "Image (*.csv)")[0]

        if ("" != filename):
            self.loadTable(self.ui.tableWidget_t, filename)


    def on_load_sigma_clicked(self):
        filename = QFileDialog.getOpenFileName(None, "Open file", "./", "Image (*.csv)")[0]

        if ("" != filename):
            self.loadTable(self.ui.tableWidget_sigma, filename)

