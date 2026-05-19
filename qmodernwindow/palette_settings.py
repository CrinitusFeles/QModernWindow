from PyQt6 import QtWidgets, QtGui, QtCore

from qmodernwindow.config import GUI_Config
from qcustomwidgets import stylesheet, Button, dark, light


class ColorPicker(QtWidgets.QWidget):
    color_updated: QtCore.pyqtSignal = QtCore.pyqtSignal(str, str, int)
    def __init__(self, label: str, color: str, num: int) -> None:
        super().__init__()
        self.num: int = num
        self.color: str = color
        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self.label = QtWidgets.QLabel(label)
        self.color_picker = QtWidgets.QToolButton()
        self._layout.addWidget(self.label)
        self._layout.addWidget(self.color_picker)
        self.color_picker.setStyleSheet(f'background-color: {color}')
        self.color_picker.clicked.connect(self.openColorDialog)

    def openColorDialog(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.color_picker.setStyleSheet(f'background-color: {self.color}')
            self.color_updated.emit(self.label.text(), self.color, self.num)

    def reset_color(self):
        p = QtWidgets.QApplication.palette()
        color = p.color(QtGui.QPalette.ColorRole(self.num))
        self.color = color.name()
        self.color_picker.setStyleSheet(f'background-color: {self.color}')

class PaletteSettings(QtWidgets.QWidget):
    def __init__(self, config: GUI_Config):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.edit_stylesheet_button = Button('Edit stylesheet')
        self.load_dark_config_button = Button('Load dark config')
        self.load_light_config_button = Button('Load light config')
        self.hlayout.addWidget(self.edit_stylesheet_button)
        self._layout.addLayout(self.hlayout)
        self.config: GUI_Config = config
        p = QtWidgets.QApplication.palette()
        self.color_widgets: dict[str, ColorPicker] = {}
        for role in QtGui.QPalette.ColorRole:
            if role in [QtGui.QPalette.ColorRole.NoRole,
                        QtGui.QPalette.ColorRole.NColorRoles]:
                continue
            color: QtGui.QBrush = getattr(p, role.name[:1].lower() + role.name[1:])()
            current_color: str = config.palette.get(role.name, color.color().name())
            color_picker = ColorPicker(role.name, current_color, role.value)
            color_picker.color_updated.connect(self.on_color_updated)
            self.color_widgets[role.name] = color_picker
            self._layout.addWidget(color_picker)

    def load_dark_config(self):
        dark()
        [w.reset_color() for w in self.color_widgets.values()]
        self.config.palette = {}

    def load_light_config(self):
        light()
        [w.reset_color() for w in self.color_widgets.values()]
        self.config.palette = {}

    def on_color_updated(self, name: str, color: str, num: int):
        self.config.palette[name] = color
        p = QtWidgets.QApplication.palette()
        p.setColor(QtGui.QPalette.ColorRole(num), QtGui.QColor(color))
        QtWidgets.QApplication.setPalette(p)
        QtWidgets.QApplication.setStyle('Fusion')
        # QtWidgets.QApplication.instance().setStyleSheet(stylesheet)  # type: ignore

    def apply_current_palette(self):
        p = QtWidgets.QApplication.palette()
        for w in self.color_widgets.values():
            p.setColor(QtGui.QPalette.ColorRole(w.num), QtGui.QColor(w.color))
        QtWidgets.QApplication.setPalette(p)
        QtWidgets.QApplication.instance().setStyleSheet(stylesheet)  # type: ignore
        QtWidgets.QApplication.setStyle('Fusion')

    def closeEvent(self, a0: QtGui.QCloseEvent | None) -> None:
        if self.config.palette:
            self.config.palette = {name: w.color
                                   for name, w in self.color_widgets.items()}
        return super().closeEvent(a0)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = PaletteSettings(GUI_Config.load_gui_config())
    w.show()
    app.exec()