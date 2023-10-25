#! /bin/python
import sys
from PyQt5 import QtWidgets

from src.ui.mainwindow import MainWindow, DistributionHandler

from src.ui.uniform_controls import UniformControls
from src.uniform_distribution import UniformDistributionCreator

from src.ui.gamma_controls import GammaControls
from src.gamma_distribution import GammaDistributionCreator

from src.ui.normal_controls import NormalControls
from src.normal_distribution import NormalDistributionCreator

def main() -> int:
    qapp = QtWidgets.QApplication(sys.argv)

    handlers : dict[str, DistributionHandler] = {
        "Равномерное": DistributionHandler(UniformControls(), UniformDistributionCreator()),
        "Эрланговское": DistributionHandler(GammaControls(), GammaDistributionCreator()),
        "Нормальное": DistributionHandler(NormalControls(), NormalDistributionCreator())
    }

    window = MainWindow(handlers);
    window.show();

    return qapp.exec();

if __name__ == "__main__":
    exit(main())
