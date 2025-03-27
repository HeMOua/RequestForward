import enum
import asyncio
from functools import partial

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox, QLabel, QStyledItemDelegate
)
from PyQt6.QtGui import QColor, QBrush, QIcon, QMovie
from PyQt6.QtCore import Qt, QMetaObject, QTimer, QSize
from qasync import asyncSlot
from models.base import Backend, Group
from proxy.base import ProxyServer
from utils.base import get_app_info, ROOT, join_url
from utils.config import ConfigManager


class IconType(str, enum.Enum):
    SUCCESS = str(ROOT / "assets/success.png")
    WAIT = str(ROOT / "assets/wait.png")
    LOADING = str(ROOT / "assets/loading.gif")
    FAIL = str(ROOT / "assets/fail.png")


class RowColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # 获取该行第一个单元格的 UserRole 数据
        if index.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole) == "current-backend":
            painter.fillRect(option.rect, QColor("lightgreen"))  # 浅蓝色
        super().paint(painter, option, index)


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
        self.testing_rows = set()  # 用于跟踪当前正在测试的行

        # 添加定时器
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_info)
        self.status_timer.start(2000)

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
        self.table.setItemDelegate(RowColorDelegate())
        # 设置表格样式，移除选中行的背景色
        # self.table.setStyleSheet("""
        #     QTableWidget::item:selected {
        #         background: gray;
        #         color: black;
        #     }
        # """)

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

        # 状态标签
        status_info_container = QWidget()
        status_info_container.setContentsMargins(0, 0, 0, 0)
        status_info_layout = QHBoxLayout()
        status_info_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_info_container.setLayout(status_info_layout)
        self.status_info_icon = QLabel()
        self.status_info_text = QLabel()
        status_info_layout.addWidget(self.status_info_icon)
        status_info_layout.addWidget(self.status_info_text)
        self.set_status_info(IconType.WAIT, "空闲")
        layout.addWidget(status_info_container)

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
            test_btn.clicked.connect(lambda checked, row=row_count: self.test_backend(row))
            layout.addWidget(test_btn)
            enable_btn = QPushButton("启用")
            enable_btn.clicked.connect(lambda checked, row=row_count: self.enable_backend(row))
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

    def set_status_info(self, icon_type: IconType, text: str):
        self.status_info_icon.clear()
        self.status_info_text.setText("")

        if icon_type:
            if icon_type.value.endswith(".gif"):
                movie = QMovie(icon_type.value)
                movie.setScaledSize(QSize(20, 20))
                movie.start()
                self.status_info_icon.setMovie(movie)
            else:
                self.status_info_icon.setPixmap(QIcon(icon_type.value).pixmap(QSize(20, 20)))
        if text:
            self.status_info_text.setText(text)

    def update_status_info(self):
        if self.is_loading:
            self.set_status_info(IconType.LOADING, "等待中...")
            return

        row = self.group.current_backend
        if isinstance(row, int) and row >= 0:
            url = self.table.item(row, 1).text()
            local_url = join_url(f'http://0.0.0.0:{self.port}', self.group.path)
            comment = f'{local_url} -> {url}'
            self.set_status_info(IconType.SUCCESS, comment)
        else:
            self.set_status_info(IconType.WAIT, "空闲")

    def add_backend(self):
        self.is_loading = True
        self.is_adding = True
        self.set_window_title()

        row_count = self.table.rowCount()
        self.table.setRowCount(row_count + 1)

        # 添加测试按钮
        widget = QWidget()
        layout = QHBoxLayout()
        test_btn = QPushButton("测试")
        test_btn.clicked.connect(lambda checked, row=row_count: self.test_backend(row))
        layout.addWidget(test_btn)
        enable_btn = QPushButton("启用")
        enable_btn.clicked.connect(lambda checked, row=row_count: self.enable_backend(row))
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

        self.is_loading = False

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

    def set_row_testing_status(self, row, is_testing=True):
        if row < 0 or row >= self.table.rowCount():
            return

        if is_testing:
            # 设置为测试中状态
            self.testing_rows.add(row)
            item = self.table.item(row, 2)
            item.setText("测试中...")
            item.setForeground(QColor("blue"))

            # 设置GIF动画状态
            movie = QMovie(IconType.LOADING.value)
            movie.setScaledSize(QSize(16, 16))
            movie.start()

            # 创建一个QLabel来显示GIF
            label = QLabel()
            label.setMovie(movie)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 将QLabel放入单元格
            self.table.setCellWidget(row, 2, label)
        else:
            # 移除测试中状态
            if row in self.testing_rows:
                self.testing_rows.remove(row)
            # 移除GIF动画
            self.table.removeCellWidget(row, 2)

    @asyncSlot()
    async def test_backend(self, row):
        if row < 0 or row >= self.table.rowCount():
            return False

        url = self.table.item(row, 1).text()
        if not url:
            return False

        # 设置为测试中状态
        self.set_row_testing_status(row, True)

        try:
            is_healthy = await self.proxy_server.check_backend_health(url)
            status = "正常" if is_healthy else "异常"

            # 移除测试中状态
            self.set_row_testing_status(row, False)

            # 更新状态
            item = self.table.item(row, 2)
            item.setText(status)
            if status == "正常":
                item.setForeground(QColor("green"))
            else:
                item.setForeground(QColor("red"))

            return is_healthy
        except Exception as e:
            # 发生异常时也要移除测试中状态
            self.set_row_testing_status(row, False)

            item = self.table.item(row, 2)
            item.setText("异常")
            item.setForeground(QColor("red"))

            return False

    @asyncSlot()
    async def enable_backend(self, row):
        if row < 0 or row >= self.table.rowCount():
            return

        self.is_loading = True

        # 先测试当前后端健康状态
        is_healthy = await self.test_backend(row)
        self.is_loading = False

        if is_healthy:
            self.group.current_backend = row
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
        # 禁用测试全部按钮，防止重复点击
        self.test_all_btn.setEnabled(False)

        # 获取所有需要测试的行
        tasks = []
        for row in range(self.table.rowCount()):
            # 为每一行创建测试任务
            tasks.append(self.test_backend(row))

        # 并发执行所有测试任务
        if tasks:
            await asyncio.gather(*tasks)

        # 测试完成后重新启用按钮
        self.test_all_btn.setEnabled(True)

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
        """设置指定行的背景颜色和文本样式"""
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    # 设置当前后端行的背景色
                    if row == self.group.current_backend:
                        item.setData(Qt.ItemDataRole.UserRole, "current-backend")
                    else:
                        item.setData(Qt.ItemDataRole.UserRole, None)

    def on_selection_change(self):
        """处理选择变化事件"""
        self.delete_btn.setEnabled(len(self.table.selectedItems()) > 0)
        self._set_row_color()  # 更新选中行的样式

    def update_test_all_btn(self):
        self.test_all_btn.setEnabled(self.table.rowCount() > 0)

    def cell_double_clicked(self, row, col):
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