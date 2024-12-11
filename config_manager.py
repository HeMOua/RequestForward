import configparser
from pathlib import Path
from typing import List, Dict
from models import Group, Backend
from setting import DEFAULT_PORT

class ConfigManager:
    _config = configparser.ConfigParser()
    _config_file = Path("config.ini")
    _is_loaded = False

    @classmethod
    def load_config(cls) -> List[Group]:
        if not cls._config_file.exists():
            cls._is_loaded = True
            return []
            
        cls._config.read(cls._config_file, encoding='utf-8')
        cls._is_loaded = True
        groups = []
        
        # 读取所有组信息
        for section in cls._config.sections():
            if section.startswith('group_'):
                group_id = int(section.split('_')[1])
                group = Group(
                    id=group_id,
                    path=cls._config[section]['path'],
                    alias=cls._config[section].get('alias', None),
                    health_check_path=cls._config[section]['health_check_path'],
                    backends=[],
                    current_backend=None
                )
                
                # 读取该组下的所有后端服务
                backend_count = int(cls._config[section].get('backend_count', '0'))
                current_backend_id = cls._config[section].get('current_backend_id', None)
                
                for i in range(backend_count):
                    backend_section = f'backend_{group_id}_{i}'
                    if cls._config.has_section(backend_section):
                        backend = Backend(
                            id=int(cls._config[backend_section]['id']),
                            url=cls._config[backend_section]['url'],
                            alias=cls._config[backend_section].get('alias', None)
                        )
                        group.backends.append(backend)
                        
                        # 如果是当前后端,设置为 current_backend
                        if current_backend_id and str(backend.id) == current_backend_id:
                            group.current_backend = backend
                
                groups.append(group)
        
        return groups

    @classmethod
    def save_config(cls, groups: List[Group] = None):
        cls._config = configparser.ConfigParser()
        cls._is_loaded = True
        
        for group in groups:
            group_section = f'group_{group.id}'
            cls._config[group_section] = {
                'id': str(group.id),
                'path': group.path,
                'health_check_path': group.health_check_path,
                'backend_count': str(len(group.backends))
            }
            if group.alias:
                cls._config[group_section]['alias'] = group.alias
            if group.current_backend:
                cls._config[group_section]['current_backend_id'] = str(group.current_backend.id)
            
            # 保存该组下的所有后端服务
            for i, backend in enumerate(group.backends):
                backend_section = f'backend_{group.id}_{i}'
                cls._config[backend_section] = {
                    'id': str(backend.id),
                    'url': backend.url
                }
                if backend.alias:
                    cls._config[backend_section]['alias'] = backend.alias
        
        cls.save_to_file()

    @classmethod
    def save_to_file(cls):
        """直接将缓存中的配置写入文件"""
        if not cls._is_loaded:
            return
            
        with open(cls._config_file, 'w', encoding='utf-8') as f:
            cls._config.write(f)

    @classmethod
    def get_config(cls) -> configparser.ConfigParser:
        """获取配置对象"""
        if not cls._is_loaded:
            cls.load_config()
        return cls._config

    @classmethod
    def get_port(cls) -> int:
        """获取配置的端口号"""
        if not cls._is_loaded:
            cls.load_config()
        
        if not cls._config.has_section('settings'):
            return DEFAULT_PORT
            
        return int(cls._config.get('settings', 'port', fallback=DEFAULT_PORT))
    
    @classmethod
    def save_port(cls, port: int):
        """保存端口配置"""
        if not cls._config.has_section('settings'):
            cls._config.add_section('settings')
        
        cls._config['settings']['port'] = str(port)
        cls.save_to_file()