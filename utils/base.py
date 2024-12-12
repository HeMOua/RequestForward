from typing import List

import yaml
from pathlib import Path

from models.base import Proxy, Group, Backend
from utils.settings import TITLE, VERSION, AUTHOR

ROOT = Path(__file__).parents[1]


def load_yaml(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_app_info(is_editing: bool = False):
    title = f"{TITLE} v{VERSION} by {AUTHOR}"
    return f"{title} - 未保存" if is_editing else title


class ConfigManager:


    _config = None
    _config_file = ROOT / "config/config.yml"
    _is_loaded = False

    @classmethod
    def load_config(cls):
        cls._is_loaded = True
        if not cls._config_file.exists():
            return []

        ConfigManager._config = load_yaml(ROOT / "config/config.yml")


    @classmethod
    def get_config(cls) -> List[Proxy]:
        if not cls._is_loaded:
            cls.load_config()

        proxys = []

        for port, groups in cls._config.items():
            proxy = Proxy(port=port, groups=[])
            for url, _group in groups.items():
                group = Group(
                    path=url,
                    alias=_group.get("alias"),
                    current_backend=_group.get("current_backend"),
                    backends=[]
                )
                proxy.groups.append(group)
                for _backend in _group.get("backends", []):
                    backend = Backend(
                        url=_backend.get("url"),
                        alias=_backend.get("alias")
                    )
                    group.backends.append(backend)
            proxys.append(proxy)

        return proxys

    @classmethod
    def save_config(cls, proxys: List[Proxy]):
        if not cls._is_loaded:
            return
        
        if proxys is not None:
            cls._config = cls.convert_config(proxys)

        cls._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cls._config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(cls._config, f, allow_unicode=True)

    @classmethod
    def convert_config(cls, proxys: List[Proxy]) -> dict:
        config = {}
        for proxy in proxys:
            groups = {}
            for group in proxy.groups:
                groups[group.path] = {
                    "alias": group.alias,
                    "current_backend": group.current_backend,
                    "backends": [
                        {
                            "url": backend.url,
                            "alias": backend.alias
                        }
                        for backend in group.backends
                    ]
                }
            config[proxy.port] = groups

        return config
