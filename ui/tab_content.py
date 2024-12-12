from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
import httpx
import asyncio

from models.base import Backend, Group
from proxy.base import ProxyServer
from utils.base import ConfigManager, get_app_info

class GroupTab(QWidget):
    def __init__(self, parent: QMainWindow, proxy_server: ProxyServer, group: Group):
        super().__init__(parent)
        self.group = group
        self.proxy_server = proxy_server
        
        # 标记
        self.is_loading = True
        self.is_adding = False
        self.is_editing = False

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top按钮区域
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.delete_btn = QPushButton("删除")
        self.test_all_btn = QPushButton("测试全部")
        
        self.add_btn.clicked.connect(self.add_backend)
        self.delete_btn.clicked.connect(self.delete_backend)
        self.test_all_btn.clicked.connect(self.test_all_backends)
        
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.test_all_btn)
        button_layout.addStretch()
        
        # 表格区域
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["别名", "接口路径", "状态", "操作"])

        # 添加焦点变化信号连接
        self.table.itemSelectionChanged.connect(self.on_selection_change)
        self.table.itemSelectionChanged.connect(self.check_empty_row)
        self.table.cellDoubleClicked.connect(self.cell_double_clicked)
        
        # 设置每列宽度相等
        header = self.table.horizontalHeader()
        # 表头字体加粗
        header.setStyleSheet("QHeaderView::section { font-weight: bold; }")
        for i in range(4):
            header.setSectionResizeMode(i, header.ResizeMode.Stretch)
            
        # 表格设置
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 状态标签
        self.status_label = QLabel()
        
        layout.addLayout(button_layout)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 加载现有后端
        self.load_backends()

        self.is_loading = False
        
        # 添加一个方法来获取主窗口
        self.main_window = self.get_main_window()
    
    def get_main_window(self):
        """获取主窗口实例"""
        parent = self.parent()
        while parent is not None:
            if parent.objectName() == "MainWindow":
                return parent
            parent = parent.parent()
        return None
    
    def add_backend(self):
        self.is_adding = True
        self.set_window_title()

        row_count = self.table.rowCount()
        self.table.setRowCount(row_count + 1)
        
        # 添加测试按钮
        test_btn = QPushButton("测试")
        test_btn.clicked.connect(lambda: self.test_backend(row_count))
        self.table.setCellWidget(row_count, 3, test_btn)
        
        # 添加状态单元格，设置为不可编辑
        status_item = QTableWidgetItem("未测试")
        status_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row_count, 2, status_item)
        
        # 添加可编辑的别名和接口路径单元格
        for col in range(2):
            item = QTableWidgetItem("")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_count, col, item)
        
        # 选中新添加的行
        self.table.setCurrentCell(row_count, 0)
    
    def delete_backend(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            if QMessageBox.question(
                self,
                "确认",
                "确定要删除该后端服务吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
                self.table.removeRow(current_row)
                self.save_backends()
    
    async def test_backend(self, row):
        url = self.table.item(row, 1).text()
        if not url:
            return
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                is_healthy = response.status_code == 200
                status = "正常" if is_healthy else "异常"
        except:
            status = "无法连接"
            
        self.table.item(row, 2).setText(status)
    
    def test_all_backends(self):
        for row in range(self.table.rowCount()):
            asyncio.create_task(self.test_backend(row))
    
    def on_selection_change(self):
        self.delete_btn.setEnabled(len(self.table.selectedItems()) > 0)
    
    def load_backends(self):
        for backend in self.group.backends:
            row_count = self.table.rowCount()
            self.table.setRowCount(row_count + 1)
            
            # 设置别名和接口路径为可编辑
            alias_item = QTableWidgetItem(backend.alias or "")
            alias_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_count, 0, alias_item)
            
            url_item = QTableWidgetItem(backend.url)
            url_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_count, 1, url_item)
            
            # 设置状态列为不可编辑
            status_item = QTableWidgetItem("未测试")
            status_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(row_count, 2, status_item)
            
            test_btn = QPushButton("测试")
            test_btn.clicked.connect(lambda: self.test_backend(row_count))
            self.table.setCellWidget(row_count, 3, test_btn)
    
    def save_backends(self):
        self.group.backends = []
        for row in range(self.table.rowCount()):
            alias = self.table.item(row, 0).text().strip()
            url = self.table.item(row, 1).text().strip()
            if alias and url:  # 只有当别名和接口路径都不为空时才保存
                backend = Backend(
                    id=len(self.group.backends) + 1,
                    url=url,
                    alias=alias
                )
                self.group.backends.append(backend)

        self.proxy_server.groups[self.group.id].backends = self.group.backends
        # 保存到配置文件
        ConfigManager.save_config(list(self.proxy_server.groups.values()))
    
    def set_window_title(self):
        """设置主窗口标题"""
        if self.main_window:
            title = get_app_info(self.is_editing or self.is_adding)
            self.main_window.setWindowTitle(title)

    def cell_double_clicked(self, item: QTableWidgetItem):
        self.is_editing = True
        self.set_window_title()

    def check_empty_row(self):
        if len(self.table.selectedItems()) > 0:
            return

        # 检查所有行
        for row in range(self.table.rowCount()):
            alias_item = self.table.item(row, 0)
            url_item = self.table.item(row, 1)
            
            if alias_item and url_item:
                alias = alias_item.text().strip()
                url = url_item.text().strip()
                if not (alias and url):  # 如果别名或接口路径为空
                    self.table.removeRow(row)
                    break  # 一次只删除一行，避免索引错误
        
        # 保存配置
        if self.is_editing or self.is_adding:
            self.save_backends()
            self.is_editing = False
            self.is_adding = False
            self.set_window_title()
