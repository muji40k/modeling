from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QEvent, Qt
from matplotlib.figure import Figure as MpFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib
matplotlib.use('Qt5Agg')

class MplCanvas(QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=100, navigation=True,
                 expandable=False):
        super(QWidget, self).__init__(parent)
        self._layout = QVBoxLayout(self);
        self.setLayout(self._layout)

        self.fig = MpFigure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.axes = []

        if (navigation):
            self.nav = NavigationToolbar2QT(self.canvas, self)
            self._layout.addWidget(self.nav)

        self._layout.addWidget(self.canvas)

        if (expandable):
            self.subwidget = QWidget()
            self.subcanvas = FigureCanvasQTAgg(self.fig)
            nav = NavigationToolbar2QT(self.subcanvas, self.subwidget)

            layout = QVBoxLayout(self.subwidget)
            self.subwidget.setLayout(layout)
            layout.addWidget(nav)
            layout.addWidget(self.subcanvas)
            self.shown = False

            self.canvas.installEventFilter(self)
            self.subcanvas.installEventFilter(self)
            self.subwidget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj in [self.canvas, self.subcanvas]:
            if event.type() == QEvent.MouseButtonDblClick:
                self.toggle_fullscreen()

        if obj is self.subwidget:
            if event.type() == QEvent.Close:
                self.toggle_fullscreen()
                return True


        return super().eventFilter(obj, event)

    def toggle_fullscreen(self):
        if (self.shown):
            self.subwidget.hide()
            self.show()
        else:
            self.hide()
            self.subwidget.show()

        self.shown = not self.shown

    def draw(self) -> None:
        self.canvas.draw()

