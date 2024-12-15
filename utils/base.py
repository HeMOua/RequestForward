import logging

import yaml
from pathlib import Path
from urllib.parse import urljoin

from utils.settings import TITLE, VERSION, AUTHOR

ROOT = Path(__file__).parents[1]


def load_yaml(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(file_path: Path, data):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True)


def join_url(base, *paths):
    for path in paths:
        base = urljoin(base, path)
    return base


def get_app_info(is_editing: bool = False):
    title = f"{TITLE} v{VERSION} by {AUTHOR}"
    return f"{title} - 未保存" if is_editing else title


class LoggerUtil:
    COLOR_FMT = '%(log_color)s%(asctime)s %(levelname)s [%(filename)s,%(lineno)d] - %(message)s'
    NORMAL_FMT = '%(asctime)s %(levelname)s [%(filename)s,%(lineno)d] - %(message)s'

    LOG_COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red',
    }

    def __init__(self, name: str, level: int = logging.DEBUG):
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

    def enable_console(self, level: int = None):
        level = level or self.level

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(self.NORMAL_FMT)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        return self

    def get_logger(self):
        return self.logger


LOGGER = (
    LoggerUtil('RequestForward')
    .enable_console()
    .get_logger()
)
