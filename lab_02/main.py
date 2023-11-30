#! /bin/python
import sys

from PyQt5 import QtWidgets

from src.ui.mainwinow import MainWindow


def main() -> int:
    # step : float = 0.2
    # probabilities = solve(table, step, initial_state=3)
    #  
    # draw_graph(table);
    # draw_probabilities(probabilities, step)
    qapp = QtWidgets.QApplication(sys.argv)
    window = MainWindow();
    window.show();

    return qapp.exec();


if __name__ == "__main__":
    exit(main());

