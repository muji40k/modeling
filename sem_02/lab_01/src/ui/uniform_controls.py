import sys

from PyQt5 import QtCore
from src.ui.func_controls import FuncControls

import out.uniform as uniform

class UniformControls(FuncControls):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = uniform.Ui_UniformControls()
        self.ui.setupUi(self)

        self.ui.doubleSpinBox.valueChanged.connect(self.onUpdate)
        self.ui.doubleSpinBox_2.valueChanged.connect(self.onUpdate)

    def get_label(self) -> str:
        return f"$a={self.ui.doubleSpinBox.value()}, b={self.ui.doubleSpinBox_2.value()}$";

    def parse(self) -> dict[str, float]:
        res : dict[str, float] = {}
        res["a"] = self.ui.doubleSpinBox.value();
        res["b"] = self.ui.doubleSpinBox_2.value();

        return res

    @QtCore.pyqtSlot()
    def onUpdate(self):
        if (sys.float_info.epsilon > abs(self.ui.doubleSpinBox.value() - self.ui.doubleSpinBox_2.value())):
            return;

        self.update.emit()
