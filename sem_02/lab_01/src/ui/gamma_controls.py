import sys

from PyQt5 import QtCore
from src.ui.func_controls import FuncControls

import out.gamma as gamma

class GammaControls(FuncControls):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = gamma.Ui_GammaControls()
        self.ui.setupUi(self)

        self.ui.spinBox.valueChanged.connect(self.onUpdate)
        self.ui.doubleSpinBox_2.valueChanged.connect(self.onUpdate)

    def get_label(self) -> str:
        return f"$k={self.ui.spinBox.value()}, \\lambda={self.ui.doubleSpinBox_2.value()}$";

    def parse(self) -> dict[str, float]:
        res : dict[str, float] = {}
        res["k"] = self.ui.spinBox.value();
        res["lambda"] = self.ui.doubleSpinBox_2.value();

        return res

    @QtCore.pyqtSlot()
    def onUpdate(self):
        if (sys.float_info.epsilon > abs(self.ui.doubleSpinBox_2.value())):
            return;

        self.update.emit()

