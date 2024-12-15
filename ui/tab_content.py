from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox
)
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import Qt, QMetaObject, QTimer
import asyncio
from qasync import asyncSlot
from models.base import Backend, Group
from proxy.base import ProxyServer
from utils.base import get_app_info
from utils.config import ConfigManager


class GroupTab(QWidget):
    def __init__(self, parent: QMainWindow, proxy_server: ProxyServer, port: int, group: Group):
        super().__init__(parent)
        self.port = port
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
        self.add_btn.clicked.connect(self.add_backend)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_backend)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        self.test_all_btn = QPushButton("测试全部")
        self.test_all_btn.clicked.connect(self.test_all_backends)
        self.test_all_btn.setEnabled(False)
        button_layout.addWidget(self.test_all_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

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

        layout.addWidget(self.table, 1)

        self.setLayout(layout)

        # 加载现有后端
        self._load_backends()
        self._set_row_color()
        self.update_test_all_btn()
        self.is_loading = False

        # 添加一个方法来获取主窗口
        self.main_window = self._get_main_window()

    def _load_backends(self):
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

            widget = QWidget()
            layout = QHBoxLayout()
            test_btn = QPushButton("测试")
            test_btn.clicked.connect(lambda: self.test_backend(widget=self.sender()))
            layout.addWidget(test_btn)
            enable_btn = QPushButton("启用")
            enable_btn.clicked.connect(lambda: self.enable_backend(self.sender()))
            layout.addWidget(enable_btn)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.table.setCellWidget(row_count, 3, widget)

    def _get_main_window(self):
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
        widget = QWidget()
        layout = QHBoxLayout()
        test_btn = QPushButton("测试")
        test_btn.clicked.connect(lambda: self.test_backend(widget=self.sender()))
        layout.addWidget(test_btn)
        enable_btn = QPushButton("启用")
        enable_btn.clicked.connect(lambda: self.enable_backend(self.sender()))
        layout.addWidget(enable_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        self.table.setCellWidget(row_count, 3, widget)

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

        self.update_test_all_btn()

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

                self.update_test_all_btn()

    def get_widget_row(self, widget):
        # 获取指定 widget 所在的行
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 3)
            if cell_widget == widget:
                return row
        return -1

    @asyncSlot()
    async def test_backend(self, row=None, widget: QPushButton = None):
        if row is None:
            row = self.get_widget_row(widget.parent())
            if row == -1:
                return

        url = self.table.item(row, 1).text()
        if not url:
            return

        is_healthy = await self.proxy_server.check_backend_health(url)
        status = "正常" if is_healthy else "异常"

        item = self.table.item(row, 2)
        item.setText(status)
        if status == "正常":
            item.setForeground(QColor("green"))
        else:
            item.setForeground(QColor("red"))

        return is_healthy

    @asyncSlot()
    async def enable_backend(self, widget: QPushButton = None):
        current_row = self.get_widget_row(widget.parent())
        if current_row < 0:
            return

        is_healthy = await self.test_backend(row=current_row, widget=widget)

        if is_healthy:
            self.group.current_backend = current_row
            self._set_row_color()
            self.save_backends()
        else:
            self.group.current_backend = -1
            self._set_row_color()
            def run_in_ui_thread():
                QMessageBox.warning(
                    self,
                    "警告",
                    "当前后端服务异常，无法启用！",
                    QMessageBox.StandardButton.Ok
                )
            QTimer.singleShot(0, run_in_ui_thread)

    @asyncSlot()
    async def test_all_backends(self):
        for row in range(self.table.rowCount()):
            await self.test_backend(row)

    def save_backends(self):
        self.group.backends = []
        for row in range(self.table.rowCount()):
            alias = self.table.item(row, 0).text().strip()
            url = self.table.item(row, 1).text().strip()
            if alias and url:  # 只有当别名和接口路径都不为空时才保存
                backend = Backend(
                    url=url,
                    alias=alias
                )
                self.group.backends.append(backend)

        for idx, group in enumerate(self.proxy_server.servers[self.port]):
            if group.path == self.group.path:
                self.proxy_server.servers[self.port][idx] = self.group
                break
        # 保存到配置文件
        ConfigManager.save_group(self.port, self.group)

    def set_window_title(self):
        """设置主窗口标题"""
        if self.main_window:
            title = get_app_info(self.is_editing or self.is_adding)
            self.main_window.setWindowTitle(title)

    def _set_row_color(self):
        """设置指定行的背景颜色"""
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    if row == self.group.current_backend:
                        item.setBackground(QBrush(QColor("lightgreen")))
                    else:
                        item.setBackground(QBrush(QColor("white")))

    def on_selection_change(self):
        self.delete_btn.setEnabled(len(self.table.selectedItems()) > 0)

    def update_test_all_btn(self):
        self.test_all_btn.setEnabled(self.table.rowCount() > 0)

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
            self.update_test_all_btn()
            self.save_backends()
            self.is_editing = False
            self.is_adding = False
            self.set_window_title()
