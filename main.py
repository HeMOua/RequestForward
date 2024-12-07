import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from config_manager import ConfigManager
from api import ProxyServer

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    proxy_server = ProxyServer()
    
    window = MainWindow(proxy_server)
    window.show()
    
    sys.exit(app.exec()) 