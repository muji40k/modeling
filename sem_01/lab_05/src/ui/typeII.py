from PyQt5 import uic
from src.ui.base_type import BaseTypeWidget

import src.task as task

import src.ui.init_type as init_type

import out.typeII as type

class TypeIIWidget(BaseTypeWidget):
    _methods = {init_type.TYPE_BOTTOM : task.TaskVStartValuesIIOrder,
                init_type.TYPE_TOP    : task.TaskVEndValuesIIOrder,
                init_type.TYPE_LEFT   : task.TaskXStartValuesIIOrder,
                init_type.TYPE_RIGHT  : task.TaskXEndValuesIIOrder}

    def __init__(self, itype : int, *args, **kwargs):
        super(BaseTypeWidget, self).__init__(*args, **kwargs);
        # self.ui = uic.loadUi("./ui/typeII.ui", self)
        self.ui = type.Ui_Form()
        self.ui.setupUi(self)
        self.creator = self._methods[itype]

    def getInitialValue(self) -> task.InitialValuesTask:
        return self.creator(self.ui.doubleSpinBox.value())

