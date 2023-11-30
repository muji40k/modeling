from PyQt5 import uic
from src.ui.base_type import BaseTypeWidget

import src.task as task

import src.ui.init_type as init_type

import out.typeIII as type

class TypeIIIWidget(BaseTypeWidget):
    _methods = {init_type.TYPE_BOTTOM : task.TaskVStartValuesIIIOrder,
                init_type.TYPE_TOP    : task.TaskVEndValuesIIIOrder,
                init_type.TYPE_LEFT   : task.TaskXStartValuesIIIOrder,
                init_type.TYPE_RIGHT  : task.TaskXEndValuesIIIOrder}

    def __init__(self, itype : int, *args, **kwargs):
        super(BaseTypeWidget, self).__init__(*args, **kwargs);
        # self.ui = uic.loadUi("./ui/typeIII.ui", self)
        self.ui = type.Ui_Form()
        self.ui.setupUi(self)
        self.creator = self._methods[itype]

    def getInitialValue(self) -> task.InitialValuesTask:
        return self.creator(self.ui.doubleSpinBox_alpha.value(),
                            self.ui.doubleSpinBox_u0.value())

