#! /bin/python
import sys

from PyQt5 import QtWidgets

from src.ui.mainwindow import MainWindow, Range

from src.randomizers.system import SystemRandomizerCreator
from src.randomizers.linear_congruent import LinearCongruentRandomCreator
from src.randomizers.table import TableRandomCreator

from src.checkers.chi2 import Chi2RandomChecker


def main() -> int:
    qapp = QtWidgets.QApplication(sys.argv)
    window = MainWindow([Range("1", 0,   9),
                         Range("2", 00,  99),
                         Range("3", 000, 999)],
                        Chi2RandomChecker(),
                        [("Системный", SystemRandomizerCreator()),
                         ("Линейный Конгруэнтный", LinearCongruentRandomCreator(1103515245, 12345, 2 ** 32)),
                         ("Табличный", TableRandomCreator("random.txt"))
                         ]);
    window.show();

    return qapp.exec();


if __name__ == "__main__":
    exit(main());

