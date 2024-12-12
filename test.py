from proxy.base import ProxyServer
from utils.base import ConfigManager


if __name__ == '__main__':
    config = ConfigManager.get_config()
    proxy_server = ProxyServer(config)
