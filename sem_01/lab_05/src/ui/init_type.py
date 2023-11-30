from PyQt5 import QtWidgets, uic

from src.ui.base_type import BaseTypeWidget

import src.task as task

import out.type as type

TYPE_LEFT   = 0
TYPE_RIGHT  = 1
TYPE_BOTTOM = 2
TYPE_TOP    = 3

from src.ui.typeI import TypeIWidget
from src.ui.typeII import TypeIIWidget
from src.ui.typeIII import TypeIIIWidget

class InitTypeWidget(QtWidgets.QWidget):
    _widgets = [TypeIWidget, TypeIIWidget, TypeIIIWidget]

    def __init__(self, itype, *args, **kwargs):
        super(QtWidgets.QWidget, self).__init__(*args, **kwargs);
        # self.ui = uic.loadUi("./ui/type.ui", self)
        self.ui = type.Ui_Form()
        self.ui.setupUi(self)

        self.itype = itype

        self.type_widget : BaseTypeWidget = TypeIWidget(itype, parent=self)
        self.ui.verticalLayout.addWidget(self.type_widget, 1)

        self.ui.comboBox_type.activated.connect(self.on_combo_box_activated)

    def getInitialValue(self) -> task.InitialValuesTask:
        return self.type_widget.getInitialValue()

    def on_combo_box_activated(self, index):
        self.ui.verticalLayout.removeWidget(self.type_widget)
        self.type_widget.close()
        self.type_widget = self._widgets[index](self.itype, parent=self)
        self.ui.verticalLayout.addWidget(self.type_widget, 1)

