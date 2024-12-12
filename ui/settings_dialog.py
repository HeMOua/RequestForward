from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                           QHBoxLayout, QPushButton, QMessageBox)
from PyQt6.QtGui import QIntValidator
import socket

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_port=8080):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        
        layout = QFormLayout()
        
        # 端口输入框,只允许输入数字
        self.port_input = QLineEdit(str(current_port))
        self.port_input.setValidator(QIntValidator(1, 65535))
        layout.addRow("端口:", self.port_input)
        
        # 按钮
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
        port = int(self.port_input.text())
        # 检查端口是否被占用
        if self.is_port_in_use(port):
            QMessageBox.warning(self, "错误", f"端口 {port} 已被占用!")
            return
        self.accept()
    
    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except socket.error:
                return True
    
    def get_port(self):
        return int(self.port_input.text()) 