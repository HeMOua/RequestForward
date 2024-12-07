from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTabBar, QWidget, QVBoxLayout, QLabel, QPushButton
)

class CustomTabBar(QTabBar):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setStyleSheet("""
            QTabBar::tab {
                width: 100px;  /* 默认宽度，确保所有 Tab 平分 */
                height: 30px;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: lightblue; /* 选中 Tab 背景 */
            }
            QTabBar::tab:!selected {
                background: lightgray; /* 未选中 Tab 背景 */
            }
            QTabBar::close-button {
                image: url(); /* 默认隐藏关闭按钮 */
                subcontrol-origin: padding;
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                image: url(close.png); /* 鼠标悬浮时显示关闭按钮图标 */
            }
        """)

    def enterEvent(self, event):
        """鼠标进入事件：显示关闭按钮"""
        self.setStyleSheet("""
            QTabBar::close-button {
                image: url(close.png); /* 替换为关闭按钮的图片路径 */
                subcontrol-origin: padding;
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                image: url(close_hover.png); /* 鼠标悬浮时的关闭按钮图标 */
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件：隐藏关闭按钮"""
        self.setStyleSheet("""
            QTabBar::close-button {
                image: url(); /* 默认隐藏关闭按钮 */
                subcontrol-origin: padding;
                subcontrol-position: right;
            }
        """)
        super().leaveEvent(event)
