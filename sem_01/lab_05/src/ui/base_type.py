from abc import abstractmethod

from PyQt5 import QtWidgets

import src.task as task

class BaseTypeWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(QtWidgets.QWidget, self).__init__(*args, **kwargs);

    @abstractmethod
    def getInitialValue(self) -> task.InitialValuesTask:
        pass

