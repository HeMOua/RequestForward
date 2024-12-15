from PyQt6.QtCore import Qt, QSize, QEvent
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
                height: 30px;
            }
        """)

        # self._hover_index = -1
    #
    # def enterEvent(self, event):
    #     """鼠标进入事件"""
    #     super().enterEvent(event)
    #
    # def leaveEvent(self, event):
    #     """鼠标离开事件"""
    #     # 重置所有标签页的可关闭状态
    #     self.setTabsClosable(False)
    #     self._hover_index = -1
    #     super().leaveEvent(event)
    #
    # def mouseMoveEvent(self, event):
    #     """鼠标移动事件"""
    #     # 获取当前鼠标悬停的标签页索引
    #     index = self.tabAt(event.pos())
    #
    #     # 如果是新的标签页
    #     if index != self._hover_index:
    #         # 重置所有标签页
    #         for i in range(self.count()):
    #             self.setTabButton(i, QTabBar.ButtonPosition.RightSide, None)
    #
    #         # 仅为当前悬停的标签页设置关闭按钮
    #         if index != -1:
    #             self.setTabsClosable(True)
    #             self.setTabButton(index, QTabBar.ButtonPosition.RightSide,
    #                               self.tabButton(index, QTabBar.ButtonPosition.RightSide))
    #
    #         self._hover_index = index
    #
    #     super().mouseMoveEvent(event)
