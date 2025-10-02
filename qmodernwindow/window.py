
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QCloseEvent
from qcustomwindow import CustomWindow
from qcustomwidgets import Button, dark, light, stylesheet
from app_updater import UpdateCheckWindow
from qmodernwindow.config import GUI_Config
from qissuereporter import ReporterWindow, ViewerWindow


class ModernWindow(CustomWindow):
    def __init__(self, version: str = '',
                 config: GUI_Config | None = None) -> None:
        super().__init__()
        self.config: GUI_Config = config or GUI_Config.load_gui_config()
        self._version: str = version
        self.theme_button = Button('', [':/svg/dark', ':/svg/light'],
                                   flat=True, iterate_icons=True,
                                   tooltip='Смена цветовой палитры')
        self.theme_button.clicked.connect(self.change_theme)
        self.add_right_widget(self.theme_button)

        self.bug_report = ReporterWindow(version, self.config.issues_url,
                                         self.config.issues_token)
        self.bug_report.report_created.connect(self.bug_report.hide)
        self.report_viewer = None
        self.reporter_button = Button('', [':/svg/bug-report'], flat=True,
                                      tooltip='Создание отчета об ошибках')
        self.reporter_button.clicked.connect(self.bug_report.show)
        self.viewer_button = Button('', [':/svg/issues'], flat=True,
                                    tooltip='Просмотр отчетов об ошибках')
        self.viewer_button.clicked.connect(self.on_viewer_clicked)
        self.pin_button = Button('', [':/svg/pin'], flat=True,
                                 tooltip='Закрепить окно поверх других')
        self.pin_button.setCheckable(True)
        self.pin_button.clicked.connect(self.on_pin)
        self.add_right_widget(self.pin_button)
        if self.config.issues_url:
            self.add_right_widget(self.reporter_button)
            self.add_right_widget(self.viewer_button)
        self.app_updater: UpdateCheckWindow | None = None
        if version and self.config.check_for_update and self.config.url:
            self.app_updater = UpdateCheckWindow(self.config.url,
                                                 self.config.token, version)
            self.app_updater.widget.new_version.connect(self.on_new_version)
        if version:
            self.version_button = Button(f"v{version}")
            self.version_button.clicked.connect(self.on_version_clicked)
            self.add_left_widget(self.version_button)

        app = QtWidgets.QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)  # type: ignore
        self.is_dark: bool = False
        if self.config.dark_theme:
            self.theme_button.click()
        else:
            light()
        if self.config.width > 0 and self.config.height > 0:
            self.resize(self.config.width, self.config.height)

    def on_viewer_clicked(self):
        if not self.report_viewer:
            self.report_viewer = ViewerWindow(self.config.issues_url,
                                              self.config.issues_token)
        self.report_viewer.show()

    def on_new_version(self):
        new_version_button = Button(f'v{self._version}',
                                    [':/svg/download-cloud'],
                                    icon_position='right')
        new_version_button.styleDict['default']['background-color'] = "#FF9224"
        new_version_button.styleDict['default']['color'] = "#000000"
        new_version_button.set_current_icon_color('#000000')
        new_version_button.clicked.connect(self.on_version_clicked)
        self.titlebar.left_layout.replaceWidget(self.version_button,
                                                new_version_button)

    def on_version_clicked(self):
        if self.app_updater:
            if self.app_updater.isVisible():
                self.app_updater.close()
            else:
                self.app_updater.show()

    def on_pin(self):
        if self.pin_button.isChecked():
            self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | self.windowFlags())
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def change_theme(self):
        light() if self.is_dark else dark()
        self.is_dark = not self.is_dark

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.config.is_maximized = self.isMaximized()
        if not self.config.is_maximized:
            self.config.width = self.width()
            self.config.height = self.height()
        self.config.dark_theme = self.is_dark
        self.config.save_config()
        super().closeEvent(a0)
        QtWidgets.QApplication.closeAllWindows()


if __name__ == '__main__':
    from qmodernwindow import __version__
    import qasync
    import asyncio
    import signal

    app: QtWidgets.QApplication = QtWidgets.QApplication([])
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    config = GUI_Config.load_gui_config()
    config.issues_url = 'https://api.github.com/repos/CrinitusFeles/QModernWindow/issues'
    w: ModernWindow = ModernWindow(__version__, config)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    w.show()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())