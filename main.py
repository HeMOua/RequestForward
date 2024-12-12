import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.base import ConfigManager
from proxy.base import ProxyServer


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    proxy_server = ProxyServer(ConfigManager.get_config())
    
    window = MainWindow(proxy_server)
    window.show()
    
    sys.exit(app.exec()) 