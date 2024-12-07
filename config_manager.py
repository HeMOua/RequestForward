import configparser
from pathlib import Path
from typing import List, Dict
from models import Group, Backend

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
                    backends=[]
                )
                
                # 读取该组下的所有后端服务
                backend_count = int(cls._config[section].get('backend_count', '0'))
                for i in range(backend_count):
                    backend_section = f'backend_{group_id}_{i}'
                    if cls._config.has_section(backend_section):
                        backend = Backend(
                            id=int(cls._config[backend_section]['id']),
                            url=cls._config[backend_section]['url'],
                            alias=cls._config[backend_section].get('alias', None)
                        )
                        group.backends.append(backend)
                
                groups.append(group)
        
        return groups

    @classmethod
    def save_config(cls, groups: List[Group] = None):
        # 直接创建新的配置对象
        cls._config = configparser.ConfigParser()
        cls._is_loaded = True  # 设置加载标志
        
        # 保存每个组的信息
        for group in groups:
            group_section = f'group_{group.id}'
            cls._config[group_section] = {
                'id': str(group.id),
                'path': group.path,
                'backend_count': str(len(group.backends))
            }
            if group.alias:
                cls._config[group_section]['alias'] = group.alias
            
            # 保存该组下的所有后端服务
            for i, backend in enumerate(group.backends):
                backend_section = f'backend_{group.id}_{i}'
                cls._config[backend_section] = {
                    'id': str(backend.id),
                    'url': backend.url
                }
                if backend.alias:
                    cls._config[backend_section]['alias'] = backend.alias
        
        # 写入文件
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