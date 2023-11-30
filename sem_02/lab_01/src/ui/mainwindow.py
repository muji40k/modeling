from PyQt5 import QtCore, QtWidgets
import numpy as np

import out.mainwindow as mainwindow
import src.ui.graph as graph

from src.ui.func_controls import FuncControls
from src.distribution import Distribution, DistributionCreator

class DistributionHandler:
    def __init__(self, controller : FuncControls, creator : DistributionCreator):
        self.controller : FuncControls = controller
        self.creator : DistributionCreator = creator


class MainWindow(QtWidgets.QWidget):
    def __init__(self, handlers : dict[str, DistributionHandler], *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs);

        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.figure = graph.MplCanvas(self)
        self.figure.axes.append(self.figure.fig.add_subplot(1, 2, 1))
        self.figure.axes.append(self.figure.fig.add_subplot(1, 2, 2))

        for name in handlers.keys():
            self.ui.comboBox_type.addItem(name);

        self.handlers = handlers;
        self.handler = next(iter(handlers.values()));

        self.handler.controller.update.connect(self.onUpdate)
        self.ui.comboBox_type.activated.connect(self.onTypeChanged)
        self.ui.doubleSpinBox.valueChanged.connect(self.onUpdate)
        self.ui.doubleSpinBox_2.valueChanged.connect(self.onUpdate)

        self.ui.verticalLayout.addWidget(self.figure)
        self.ui.verticalLayout.addWidget(self.handler.controller)

        self.ui.verticalLayout.setStretch(2, 1)

        self.draw_plot()


    def draw_plot(self):
        x = np.linspace(self.ui.doubleSpinBox.value(), self.ui.doubleSpinBox_2.value(), 1000);
        distribution = self.handler.creator.create(self.handler.controller.parse());
        pdf = [distribution.pdf(i) for i in x]
        cdf = [distribution.cdf(i) for i in x]

        for axes in self.figure.axes:
            axes.cla()
            axes.grid(True)
            axes.set_xlabel("X")

        legend = self.handler.controller.get_label()

        self.figure.axes[0].plot(x, pdf, label=legend)
        self.figure.axes[1].plot(x, cdf, label=legend)

        self.figure.axes[0].set_ylabel("Функция плотности распределения")
        self.figure.axes[1].set_ylabel("Функция распределения")

        self.figure.axes[0].legend()
        self.figure.axes[1].legend()

        self.figure.draw()


    @QtCore.pyqtSlot()
    def onTypeChanged(self):
        self.handler.controller.update.disconnect(self.onUpdate)
        name = self.ui.comboBox_type.currentText()
        self.ui.verticalLayout.removeWidget(self.handler.controller)
        self.handler.controller.hide()
        self.handler = self.handlers[name]
        self.handler.controller.update.connect(self.onUpdate)
        self.ui.verticalLayout.addWidget(self.handler.controller)
        self.handler.controller.show();
        self.draw_plot();


    @QtCore.pyqtSlot()
    def onUpdate(self):
        self.draw_plot()

