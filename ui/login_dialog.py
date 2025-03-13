from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QMessageBox, QFormLayout)
from PySide6.QtCore import Qt
from utils.db import DatabaseManager

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """設置登入對話框UI"""
        self.setWindowTitle("會計底稿處理系統 - 登入")
        self.setFixedSize(400, 300)
        
        # 主佈局
        layout = QVBoxLayout()
        
        # 標題
        title_label = QLabel("會計底稿處理系統")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        
        # 登入表單
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("請輸入用戶名")
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("請輸入密碼")
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("用戶名:", self.username_edit)
        form_layout.addRow("密碼:", self.password_edit)
        
        # 登入按鈕
        self.login_button = QPushButton("登入")
        self.login_button.setFixedHeight(40)
        self.login_button.clicked.connect(self.attempt_login)
        
        # 版本信息
        version_label = QLabel("© 2025 會計底稿處理系統 | 版本 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: gray; font-size: 12px; margin-top: 20px;")
        
        # 添加所有元素到佈局
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.login_button)
        layout.addWidget(version_label)
        
        self.setLayout(layout)
    
    def attempt_login(self):
        """嘗試登入"""
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        # 在實際應用中應進行更複雜的驗證和密碼加密
        if not username or not password:
            QMessageBox.warning(self, "登入失敗", "用戶名和密碼不能為空")
            return
        
        # 連接資料庫驗證用戶
        db = DatabaseManager()
        user = db.authenticate_user(username, password)
        
        if user:
            self.user_data = user
            self.accept()  # 關閉對話框，返回True
        else:
            QMessageBox.warning(self, "登入失敗", "用戶名或密碼錯誤")
    
    def get_user(self):
        """獲取登入用戶資料"""
        return self.user_data