from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure as MpFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib
matplotlib.use('Qt5Agg')

class MplCanvas(QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(QWidget, self).__init__(parent)
        self._layout = QVBoxLayout(self);
        self.setLayout(self._layout)

        self.fig = MpFigure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.axes = []
        self.nav = NavigationToolbar2QT(self.canvas, self)

        self._layout.addWidget(self.nav)
        self._layout.addWidget(self.canvas)

    def draw(self) -> None:
        self.canvas.draw()

