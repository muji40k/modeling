from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

from dataclasses import dataclass

from src.randomizer import RandomizerCreator, RandomChecker

import out.mainwindow as mainwindow

SEQUENCE_SIZE = 1000


@dataclass
class Range:
    name: str
    min: int
    max: int


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,
                 ranges: list[Range],
                 checker: RandomChecker,
                 randomizers: list[tuple[str, RandomizerCreator]],
                 *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs);
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.checker = checker

        for item in ranges:
            self.ui.comboBox_capacity.addItem(item.name, item)

        for item in randomizers:
            self.ui.comboBox_method.addItem(item[0], item[1])

        self.rand_sequence : list[int] = [0 for _ in range(SEQUENCE_SIZE)]

        self.setup_table()
        self.fill_method_column()
        self.check(self.rand_sequence, self.ui.tableWidget.item(10, 0))

        self.ui.pushButton_generate.clicked.connect(self.onPuchButtonClicked)
        self.ui.tableWidget.cellChanged.connect(self.onCellChanged)


    def setup_table(self) -> None:
        for j in range(2):
            for i in range(10):
                item = QTableWidgetItem("0");

                if (0 == j):
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable);

                self.ui.tableWidget.setItem(i, j, item);

            item = QTableWidgetItem("0");
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable);
            self.ui.tableWidget.setItem(10, j, item);


    def get_range(self) -> tuple[int, int]:
        handle = self.ui.comboBox_capacity.currentData()

        return handle.min, handle.max


    def fill_method_column(self) -> None:
        creator = self.ui.comboBox_method.currentData()
        randomizer = creator.create(*self.get_range())

        for i in range(SEQUENCE_SIZE):
            num = randomizer.get()

            if (10 > i):
                self.ui.tableWidget.item(i, 0).setText(str(num))

            self.rand_sequence[i] = num


    def read_user_column(self) -> list[int]:
        out : list[int] = [0 for _ in range(10)]

        try:
            for i in range(10):
                out[i] = int(self.ui.tableWidget.item(i, 1).text())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Ошибка")
            msg.setText("Значения выборки - целые числа")
            msg.exec_()

        return out


    def onCellChanged(self, i: int, j: int) -> None:
        if (1 != j or 10 == i):
            return

        self.check(self.read_user_column(), self.ui.tableWidget.item(10, 1))


    def onPuchButtonClicked(self) -> None:
        self.fill_method_column()
        self.check(self.rand_sequence, self.ui.tableWidget.item(10, 0))


    def check(self, sequence: list[int], item: QTableWidgetItem) -> None:
        item.setText("{:0.6g}".format(self.checker.check(sequence)))

