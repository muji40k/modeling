from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem

import random

import out.mainwinow as mainwindow
import src.ui.graph as graph

import src.draw as draw
import src.markov as markov

TIME_STEP = 1e-3
EPS = 1e-5

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs);

        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.figure_model = graph.MplCanvas(self, navigation=False, expandable=True)
        self.figure_graph = graph.MplCanvas(self, expandable=True)

        self.figure_model.axes.append(self.figure_model.fig.add_subplot(1, 1, 1))
        self.figure_graph.axes.append(self.figure_graph.fig.add_subplot(1, 1, 1))

        self.ui.gridLayout.addWidget(self.figure_model, 0, 1, 2, 1);
        self.ui.gridLayout.setColumnStretch(0, 1)
        self.ui.verticalLayout_5.addWidget(self.figure_graph);

        self.build_table()
        self.redraw_graph()

        self.ui.spinBox_states.valueChanged.connect(self.refresh_table)
        self.ui.tableWidget_model.itemChanged.connect(self.redraw_graph)
        self.ui.spinBox_states.valueChanged.connect(self.redraw_graph)
        self.ui.pushButton_calculate.clicked.connect(self.calculate)
        self.ui.pushButton_fill.clicked.connect(self.generate_table)

        self.ui.tableWidget_result.verticalHeader().hide()


    def calculate(self):
        table = self.read_table()

        if (0 == len(table)):
            return

        probabilities = markov.solve(table)
        probabilities_g, times = markov.simulate(table, TIME_STEP, 0, -1, EPS)

        draw.draw_probabilities(probabilities_g, TIME_STEP, self.figure_graph.axes[0])
        self.figure_graph.draw()
        self.fill_res_table(probabilities, times)
        # print(markov.find_times(table, probabilities))


    def fill_res_table(self, probabilities, times):
        self.ui.tableWidget_result.setRowCount(0)

        for i in range(self.states):
            self.ui.tableWidget_result.insertRow(i)
            self.ui.tableWidget_result.setItem(i, 0, QTableWidgetItem(str(i)))
            self.ui.tableWidget_result.setItem(i, 1, QTableWidgetItem("{:0.6g}".format(probabilities[i])))
            self.ui.tableWidget_result.setItem(i, 2, QTableWidgetItem("{:0.6g}".format(times[i])))


    def redraw_graph(self):
        table = self.read_table()

        if (0 == len(table)):
            return

        draw.draw_graph(table, self.figure_model.axes[0], 0)
        self.figure_model.draw()


    def read_table(self):
        try:
            out : list[list[float]] = []

            for i in range(self.states):
                row : list[float] = [0 for _ in range(self.states)]

                for j in range(self.states):
                    text = self.ui.tableWidget_model.item(i, j).text()

                    if ("" != text):
                        row[j] = float(text)

                out.append(row)

            return out;
        except ValueError:
            return []


    def generate_table(self):
        self.ui.tableWidget_model.itemChanged.disconnect(self.redraw_graph)

        for i in range(self.states):
            for j in range(self.states):
                if (i != j):
                    self.ui.tableWidget_model.setItem(i, j, QTableWidgetItem("0.0"))

            checked = [False for _ in range(self.states)]
            line : list[float] = [0 for _ in range(self.states)]

            line[i] = random.random()

            for j in range(random.randint(1, self.states - 1)):
                k = random.randint(0, self.states - 1)

                while checked[k] or k == i:
                    k = (k + 1) % self.states

                checked[k] = True
                line[k] = random.random()

            s = sum(line)

            for j in range(self.states):
                if (i != j):
                    self.ui.tableWidget_model.setItem(i, j, QTableWidgetItem("{:0.3g}".format(line[j] / s)))

        self.ui.tableWidget_model.itemChanged.connect(self.redraw_graph)
        self.redraw_graph()


    def refresh_table(self):
        states = self.ui.spinBox_states.value()

        if (states == self.states):
            return

        self.ui.tableWidget_model.itemChanged.disconnect(self.redraw_graph)

        self.ui.tableWidget_model.setRowCount(states)
        self.ui.tableWidget_model.setColumnCount(states)

        if (states > self.states):
            for i in range(self.states, states):
                self.ui.tableWidget_model.setHorizontalHeaderItem(i, QTableWidgetItem(str(i)))
                self.ui.tableWidget_model.setVerticalHeaderItem(i, QTableWidgetItem(str(i)))

            for i in range(self.states):
                for j in range(self.states, states):
                    self.ui.tableWidget_model.setItem(i, j, QTableWidgetItem("0.0"))
                    self.ui.tableWidget_model.setItem(j, i, QTableWidgetItem("0.0"))

            for i in range(self.states, states):
                for j in range(self.states, states):
                    item = QTableWidgetItem()

                    if (i == j):
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable);
                    else:
                        item.setText("0.0")

                    self.ui.tableWidget_model.setItem(i, j, item)

        self.states = states;

        self.ui.tableWidget_model.itemChanged.connect(self.redraw_graph)
        self.redraw_graph()


    def build_table(self):
        size = self.ui.spinBox_states.value()
        self.ui.tableWidget_model.clear()

        for i in range(size):
            self.ui.tableWidget_model.insertRow(i)
            self.ui.tableWidget_model.insertColumn(i)
            self.ui.tableWidget_model.setHorizontalHeaderItem(i, QTableWidgetItem(str(i)))
            self.ui.tableWidget_model.setVerticalHeaderItem(i, QTableWidgetItem(str(i)))

        for i in range(size):
            for j in range(size):
                item = QTableWidgetItem()

                if (i == j):
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable);
                else:
                    item.setText("0.0")

                self.ui.tableWidget_model.setItem(i, j, item)

        self.states = size

