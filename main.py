import sys
import asyncio

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from ui.main_window import MainWindow
from proxy.base import ProxyServer
from utils.config import ConfigManager
from utils.base import ROOT


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(str(ROOT / "assets/favor.ico")))

    # 将 asyncio 的事件循环集成到 PyQt 中
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 创建 ProxyServer 和 MainWindow 实例
    proxy_server = ProxyServer(ConfigManager.get_config())
    window = MainWindow(proxy_server)
    window.show()

    # 在集成的事件循环中启动协程
    with loop:  # 确保事件循环正确关闭
        asyncio.ensure_future(proxy_server.start_servers())  # 非阻塞地启动协程
        sys.exit(loop.run_forever())