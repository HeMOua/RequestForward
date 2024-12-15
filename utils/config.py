from typing import List
from pathlib import Path

from models.base import Proxy, Group, Backend
from utils.base import load_yaml, save_yaml

ROOT = Path(__file__).parents[1]


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
    def save_config(cls, proxys: List[Proxy] = None):
        if not cls._is_loaded:
            return

        if proxys is not None:
            cls._config = cls._convert_config(proxys)

        save_yaml(cls._config_file, cls._config)

    @classmethod
    def save_group(cls, port: int, group: Group):
        if not cls._is_loaded:
            return

        if port not in cls._config:
            cls._config[port] = {}

        cls._config[port][group.path] = {
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

        cls.save_config()

    @classmethod
    def save_backends(cls, port: int, path: str, backends: List[Backend]):
        if not cls._is_loaded:
            return

        if port not in cls._config:
            cls._config[port] = {}

        if path not in cls._config[port]:
            cls._config[port][path] = {}

        cls._config[port][path]["backends"] = [
            {
                "url": backend.url,
                "alias": backend.alias
            }
            for backend in backends
        ]

        cls.save_config()

    @classmethod
    def _convert_config(cls, proxys: List[Proxy]) -> dict:
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
