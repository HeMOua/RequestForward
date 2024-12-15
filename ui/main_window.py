import sys
from pathlib import Path
from typing import List
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QHBoxLayout,
    QPushButton,
    QDialog,
    QLineEdit,
    QFormLayout,
    QMessageBox,
    QSizePolicy
)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt

from proxy.base import ProxyServer
from models.base import Group, Proxy
from ui.custom_tab import CustomTabBar
from ui.tab_content import GroupTab
from utils.base import get_app_info, ROOT
from utils.config import ConfigManager


class AddGroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新组")
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.port_input = QLineEdit()
        self.port_input.setValidator(QIntValidator(1, 65535))  # 限制只能输入1-65535的端口号
        self.path_input = QLineEdit()
        self.alias_input = QLineEdit()
        self.health_check_path_input = QLineEdit()
        
        layout.addRow("端口 *:", self.port_input)
        layout.addRow("路径 *:", self.path_input)
        layout.addRow("  别名:", self.alias_input)
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        
        save_btn.clicked.connect(self.on_save)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def on_save(self):
        # 校验逻辑
        if not self.port_input.text().strip():
            QMessageBox.warning(self, "错误", "端口不能为空！")
            return
        if not self.path_input.text().strip():
            QMessageBox.warning(self, "错误", "路径不能为空！")
            return
        
        # 校验通过，关闭弹窗
        self.accept()


    def get_values(self):
        return {
            'port': self.port_input.text(),
            'path': self.path_input.text(),
            'alias': self.alias_input.text()
        }


class MainWindow(QMainWindow):
    def __init__(self, proxy_server: ProxyServer):
        super().__init__()
        self.setObjectName("MainWindow")
        self.proxy_server = proxy_server
        
        self.setWindowTitle(get_app_info())
        self.resize(800, 600)
        
        # 创建主标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(CustomTabBar())
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.tab_widget)

        # 添加新标签页按钮
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setFixedSize(30, 30)
        self.add_tab_button.clicked.connect(self.show_add_group_dialog)
        self.tab_widget.setCornerWidget(self.add_tab_button, Qt.Corner.TopRightCorner)
        self.tab_widget.cornerWidget(Qt.Corner.TopRightCorner).setStyleSheet("""
        QPushButton {
            width: 30px;
            height: 30px;
            padding: 0;
            border: 0;
            margin: 1px;
            margin-right: 0px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #fbfbfb;
        }
        QPushButton:hover {
            background-color: #f6f6f6;
        }
        """)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabBar().setExpanding(True)

        # 加载已有配置
        self.load_groups()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("设置")
        port_action = settings_menu.addAction("端口设置")
        about_menu = menubar.addMenu("关于")

    def show_add_group_dialog(self):
        dialog = AddGroupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            port = int(values['port'])

            groups = self.proxy_server.servers.get(port, [])

            # 创建新组
            group = Group(
                path=values['path'],
                alias=values['alias'] if values['alias'] else None,
                backends=[]
            )

            groups.append(group)
            
            # 添加新标签页
            self.add_group_tab(port, group)
            
            # 更新代理服务器
            self.proxy_server.servers[port] = groups
            self.proxy_server.restart_server()

            # 保存配置
            self.save_config()
    
    def add_group_tab(self, port: int, group: Group):
        tab = GroupTab(self, self.proxy_server, port, group)
        tab_name = f"[{group.alias}] - {port}{group.path}" if group.alias else f"{port}{group.path}"
        self.tab_widget.addTab(tab, tab_name)

    def close_tab(self, index):
        if QMessageBox.question(
            self,
            "确认",
            "确定要删除该组吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            tab: GroupTab = self.tab_widget.widget(index)
            select_group: Group = tab.group
            
            # 从代理服务器中移除
            groups: List[Group] = self.proxy_server.servers[tab.port]
            for group in groups:
                if group.path == select_group.path:
                    groups.remove(group)
                    break

            if not groups or len(groups) <= 0:
                del self.proxy_server.servers[tab.port]
            
            # 移除标签页
            self.tab_widget.removeTab(index)

            # 重启代理服务器
            self.proxy_server.restart_server()

            # 保存配置
            self.save_config()
    
    def load_groups(self):
        proxys = ConfigManager.get_config()
        for proxy in proxys:
            for group in proxy.groups:
                self.add_group_tab(proxy.port, group)
    
    def save_config(self):
        proxys = [
            Proxy(port=port, groups=groups) for port, groups in self.proxy_server.servers.items()
        ]
        ConfigManager.save_config(proxys)

