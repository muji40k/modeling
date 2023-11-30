from PyQt5 import uic
from src.ui.base_type import BaseTypeWidget

import src.task as task

import src.ui.init_type as init_type

import out.typeI as type

class TypeIWidget(BaseTypeWidget):
    _methods = {init_type.TYPE_BOTTOM : task.StartValuesIOrder,
                init_type.TYPE_TOP    : task.EndValuesIOrder,
                init_type.TYPE_LEFT   : task.StartValuesIOrder,
                init_type.TYPE_RIGHT  : task.EndValuesIOrder}

    def __init__(self, itype : int, *args, **kwargs):
        super(BaseTypeWidget, self).__init__(*args, **kwargs);
        # self.ui = uic.loadUi("./ui/typeI.ui", self)
        self.ui = type.Ui_Form()
        self.ui.setupUi(self)
        self.creator = self._methods[itype]

    def getInitialValue(self) -> task.InitialValuesTask:
        return self.creator(self.ui.doubleSpinBox.value())

