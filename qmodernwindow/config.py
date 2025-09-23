from pathlib import Path
from typing import Self

from loguru import logger
from pydantic import BaseModel


class GUI_Config(BaseModel):
    dark_theme: bool = False
    check_for_update: bool = True
    token: str = ''
    url: str = ''
    width: int = 0
    height: int = 0

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
                return cls.model_validate_json(raw_config)
        else:
            logger.debug('GUI Config was not found. Created default config')
            config = cls()
            config.save_config()
            return config
