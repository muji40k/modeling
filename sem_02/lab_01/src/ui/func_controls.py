from PyQt5 import QtCore, QtWidgets

class FuncControls(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def get_label(self) -> str:
        return ""

    def parse(self) -> dict[str, float]:
        return {}

    update = QtCore.pyqtSignal()

