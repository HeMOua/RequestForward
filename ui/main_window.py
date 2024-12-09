from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTableWidget,
                           QDialog, QLineEdit, QFormLayout, QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, QEvent
from api import ProxyServer
from models import Group, Backend
from ui.tab_content import GroupTab
from ui.custom_tab import CustomTabBar
from config_manager import ConfigManager
import uuid

from utils import get_app_info

class AddGroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新组")
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.path_input = QLineEdit()
        self.alias_input = QLineEdit()
        self.health_check_path_input = QLineEdit()
        
        layout.addRow("路径 *:", self.path_input)
        layout.addRow("别名:", self.alias_input)
        layout.addRow("健康检查路径 *:", self.health_check_path_input)
        
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
        if not self.path_input.text().strip():
            QMessageBox.warning(self, "错误", "路径不能为空！")
            return
        if not self.health_check_path_input.text().strip():
            QMessageBox.warning(self, "错误", "健康检查路径不能为空！")
            return
        
        # 校验通过，关闭弹窗
        self.accept()


    def get_values(self):
        return {
            'path': self.path_input.text(),
            'alias': self.alias_input.text(),
            'health_check_path': self.health_check_path_input.text()
        }

class MainWindow(QMainWindow):
    def __init__(self, proxy_server: ProxyServer):
        super().__init__()
        self.setObjectName("MainWindow")
        self.proxy_server = proxy_server
        
        self.setWindowTitle(get_app_info())
        self.resize(800, 600)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建主标签页
        self.tab_widget = QTabWidget()
        # self.tab_widget.setTabBar(CustomTabBar())
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(True)
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 添加新标签页按钮
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setFixedSize(20, 20)
        self.add_tab_button.clicked.connect(self.show_add_group_dialog)
        self.tab_widget.setCornerWidget(self.add_tab_button, Qt.Corner.BottomRightCorner)
        
        # 标签页关闭信号
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        self.setCentralWidget(self.tab_widget)
        
        # 加载已有配置
        self.load_groups()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("设置")
        about_menu = menubar.addMenu("关于")
    
    def show_add_group_dialog(self):
        dialog = AddGroupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()

            # 创建新组
            group = Group(
                id=len(self.proxy_server.groups) + 1,
                path=values['path'],
                alias=values['alias'] if values['alias'] else None,
                health_check_path=values['health_check_path'],
                backends=[]
            )
            
            # 添加新标签页
            self.add_group_tab(group)
            
            # 更新代理服务器
            self.proxy_server.groups[group.id] = group
            
            # 保存配置
            self.save_config()
    
    def add_group_tab(self, group: Group):
        tab = GroupTab(self, self.proxy_server, group)
        tab_name = f"[{group.alias}] - {group.path}" if group.alias else group.path
        self.tab_widget.addTab(tab, tab_name)
    
    def close_tab(self, index):
        if QMessageBox.question(
            self,
            "确认",
            "确定要删除该组吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            tab = self.tab_widget.widget(index)
            group = tab.group
            
            # 从代理服务器中移除
            self.proxy_server.groups.pop(group.id, None)
            self.proxy_server.group_backends.pop(group.path, None)
            
            # 移除标签页
            self.tab_widget.removeTab(index)
            
            # 保存配置
            self.save_config()
    
    def load_groups(self):
        groups = ConfigManager.load_config()
        for group in groups:
            self.add_group_tab(group)
            self.proxy_server.groups[group.id] = group
    
    def save_config(self):
        groups = list(self.proxy_server.groups.values())
        ConfigManager.save_config(groups)
    
    def eventFilter(self, obj, event):
        if obj == self.tab_widget.tabBar():
            if event.type() == event.Type.HoverEnter:
                # 获取鼠标下的标签索引
                index = self.tab_widget.tabBar().tabAt(event.pos())
                if index >= 0:
                    self.tab_widget.setTabsClosable(True)
            elif event.type() == event.Type.HoverLeave:
                self.tab_widget.setTabsClosable(False)
        return super().eventFilter(obj, event)