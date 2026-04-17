from pathlib import Path
import sys
from typing import Self

from PyQt6 import QtWidgets
from loguru import logger
from pydantic import BaseModel


def show_dialog():
    msg = QtWidgets.QMessageBox()
    msg_btn = QtWidgets.QMessageBox.StandardButton
    msg.setStandardButtons(msg_btn.Yes | msg_btn.No)
    msg.setWindowTitle('Внимание!')
    msg.setText('Невозможно загрузить файл конфигурации из-за\n'\
                'неправильной/обновленной структуры.\n\n'\
                'Для использования текущего файла конфигурации необходимо исправить \n'\
                'некорректную структуру вручную, после чего перезапустить программу.\n\n'\
                'Нажмите "Yes" для перезаписи существующего файла новым валидным.\n'\
                'Все изменения в текушем файле будут потеряны.')
    msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
    style = msg.style()
    if style:
        icon = style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning)
        msg.setWindowIcon(icon)

    btn = msg.exec()
    return btn == msg_btn.Yes


class GUI_Config(BaseModel):
    dark_theme: bool = False
    check_for_update: bool = True
    token: str = ''
    url: str = ''
    issues_url: str = ''
    issues_token: str = ''
    width: int = 0
    height: int = 0
    is_maximized: bool = False

    def save_config(self) -> None:
        config_path: Path = Path.cwd() / 'app_config.json'
        with open(config_path, 'w+', encoding='utf-8') as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def load_gui_config(cls) -> Self:
        config_path: Path = Path.cwd() / 'app_config.json'
        if config_path.exists():
            with open(config_path, 'r+', encoding='utf-8') as file:
                raw_config: str = file.read()
                try:
                    return cls.model_validate_json(raw_config)
                except Exception as err:
                    logger.exception(err)
                    if show_dialog():
                        config = cls()
                        config.save_config()
                        return config
                    else:
                        sys.exit(0)

        else:
            logger.debug('GUI Config was not found. Created default config')
            config = cls()
            config.save_config()
            return config
