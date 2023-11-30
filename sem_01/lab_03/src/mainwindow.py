from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QTableWidget
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.figure import Figure as MpFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

import csv
from threading import Thread

import out.form as form

from src.task import solve, TaskHandle, Result
from misc.interpolate import TableFunc

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = MpFigure(figsize=(width, height), dpi=dpi)
        self.axes = []
        super(MplCanvas, self).__init__(self.fig)


def calc_thread(handle : TaskHandle, result : Result) -> None:
    _result = solve(handle)
    result.radius = _result.radius
    result.temperature = _result.temperature
    result.f1 = _result.f1
    result.f2 = _result.f2
    result.iter = _result.iter


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs);
        self.start = False
        self.thread : Thread
        self.result : Result = Result([], [], 0, 0, 0)


        # self.ui = uic.loadUi("./ui/form.ui", self)
        self.ui = form.Ui_MainWindow()
        self.ui.setupUi(self)

        self.figure = MplCanvas(self.ui.frame_plot)
        self.toolbar = NavigationToolbar2QT(self.figure, self.ui.frame_plot)
        self.ui.verticalLayout_plot.addWidget(self.toolbar)
        self.ui.verticalLayout_plot.addWidget(self.figure)
        self.ui.verticalLayout_plot.setStretch(0, 1)

        self.figure.axes.append(self.figure.fig.add_subplot(1, 1, 1))

        self.loadTable(self.ui.tableWidget_lambda, "res/lambda.csv")
        self.loadTable(self.ui.tableWidget_k, "res/k.csv")

        self.clear_axes();

        self.timer = QtCore.QTimer()
        self.timer.start(100)

        self.timer.timeout.connect(self.timeout)
        self.ui.pushButton_calculate.clicked.connect(self.on_calculate_clicked)
        self.ui.pushButton_load_lambda.clicked.connect(self.on_load_lambda_clicked)
        self.ui.pushButton_load_k.clicked.connect(self.on_load_k_clicked)

        self.ui.doubleSpinBox_r0.valueChanged.connect(self.reset_step)
        self.ui.doubleSpinBox_r_max.valueChanged.connect(self.reset_step)
        self.ui.spinBox_steps.valueChanged.connect(self.reset_step)

        self.reset_step()


    def timeout(self):
        if (not self.start or self.thread.is_alive()):
            return

        self.start = False
        self.thread.join()

        self.clear_axes()
        self.figure.axes[0].plot(self.result.radius, self.result.temperature)
        # self.figure.axes[0].plot([self.result.radius[0], self.result.radius[-1]], 
        #                          [self.result.temperature[0], self.result.temperature[-1]])

        # if (1e-4 > abs(max(self.result.temperature) - min(self.result.temperature))):
        #     rng = [0, max(self.result.temperature) * 1.1]
        #  
        #     if (0 > self.result.temperature[0]):
        #         rng.reverse()
        #  
        #     self.figure.axes[0].set_ylim(rng)

        self.figure.draw()
        self.ui.label_status.setText("Готово")

        self.ui.label_f1.setText("f1: {:0.6g}".format(self.result.f1))
        self.ui.label_f2.setText("f2: {:0.6g}".format(self.result.f2))
        self.ui.label_iter.setText("Число итераций: {:d}".format(self.result.iter))


    def clear_axes(self):
        # self.figure.figure.tight_layout(pad=0.5)

        for axes in self.figure.axes:
            axes.cla()
            axes.grid(True)
            axes.set_xlabel("Радиус [см]")
            axes.set_ylabel("Температура [К]")


    def on_calculate_clicked(self):
        if (self.start):
            return

        lambda_t = self.getTable(self.ui.tableWidget_lambda)
        k_t = self.getTable(self.ui.tableWidget_k)

        lambda_t_list = sorted(list(lambda_t.keys()))
        lambda_list = [lambda_t[i] for i in lambda_t_list]

        k_t_list = sorted(list(k_t.keys()))
        k_list = [k_t[i] for i in k_t_list]

        handle = TaskHandle(TableFunc(lambda_t_list, lambda_list),
                            TableFunc(k_t_list, k_list))

        handle.n = self.ui.doubleSpinBox_n.value()
        handle.r0 = self.ui.doubleSpinBox_r0.value()
        handle.r_max = self.ui.doubleSpinBox_r_max.value()
        handle.steps = self.ui.spinBox_steps.value()
        handle.t0 = self.ui.doubleSpinBox_t0.value()
        handle.sigma = 5.668e-12
        handle.f_0 = self.ui.doubleSpinBox_f0.value()
        handle.alpha = self.ui.doubleSpinBox_alpha.value()
        handle.eps1 = 10 ** self.ui.spinBox_eps1.value()
        handle.eps2 = 10 ** self.ui.spinBox_eps2.value()

        self.start = True
        self.thread = Thread(target=calc_thread, args=(handle, self.result))
        self.thread.daemon = True
        self.thread.start()
        self.ui.label_status.setText("Рассчет...")


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
        self.ui.label_step.setText("Шаг: {:0.6g}"
                                   .format((self.ui.doubleSpinBox_r_max.value() - self.ui.doubleSpinBox_r0.value()) / self.ui.spinBox_steps.value()))

