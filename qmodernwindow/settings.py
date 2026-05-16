from PyQt6 import QtWidgets, QtCore, QtGui
from qcustomwindow import CustomWindow
from qcustomwidgets import TabWidget, Button

from qmodernwindow.config import GUI_Config


class SettingsWindow(CustomWindow):
    def __init__(self, config: GUI_Config) -> None:
        super().__init__()
        self.tabs = TabWidget()
        self.config: GUI_Config = config
        self.addWidget(self.tabs)
        self.setTitle('Application settings')
        self.pin_button = Button('', [':/svg/pin', ':/svg/pinned'], flat=True,
                                 iterate_icons=True,
                                 tooltip='Закрепить окно поверх других')
        self.pin_button.setCheckable(True)
        self.pin_button.clicked.connect(self.on_pin)
        self.add_right_widget(self.pin_button)
        self._widgets: dict[str, QtWidgets.QWidget] = {}

    def add_settings_page(self, name: str, widget: QtWidgets.QWidget):
        if name not in self._widgets:
            self._widgets[name] = widget
            self.tabs.addTab(widget, name)
        else:
            raise ValueError(f'{name} already added to settings window')

    def __getitem__(self, key) -> QtWidgets.QWidget:
        return self._widgets[key]

    def on_pin(self):
        if self.pin_button.isChecked():
            self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | self.windowFlags())
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def closeEvent(self, a0: QtGui.QCloseEvent | None) -> None:
        for w in self._widgets.values():
            w.closeEvent(a0)
        return super().closeEvent(a0)