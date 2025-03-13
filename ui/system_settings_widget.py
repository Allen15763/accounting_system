import os
import csv

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTabWidget, QLineEdit, QPushButton,
                               QFormLayout, QComboBox, QCheckBox, QMessageBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QTimeEdit, QScrollArea, QSpinBox, QFileDialog)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QIcon
from utils.db import DatabaseManager


class SystemSettingsWidget(QWidget):
    """系統設置頁面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """設置系統設置UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("系統設置")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 標籤頁
        self.tab_widget = QTabWidget()
        
        # 一般設置標籤頁
        self.general_tab = QWidget()
        self.setup_general_tab()
        
        # 用戶管理標籤頁
        self.users_tab = QWidget()
        self.setup_users_tab()
        
        # 權限設置標籤頁
        self.permissions_tab = QWidget()
        self.setup_permissions_tab()
        
        # 系統日誌標籤頁
        self.logs_tab = QWidget()
        self.setup_logs_tab()
        
        # 添加標籤頁
        self.tab_widget.addTab(self.general_tab, "一般設置")
        self.tab_widget.addTab(self.users_tab, "用戶管理")
        self.tab_widget.addTab(self.permissions_tab, "權限設置")
        self.tab_widget.addTab(self.logs_tab, "系統日誌")
        
        layout.addWidget(self.tab_widget)
        
    def setup_general_tab(self):
        """設置一般設置標籤頁"""
        layout = QVBoxLayout(self.general_tab)
        
        # 一般設置卡片
        general_frame = QFrame()
        general_frame.setObjectName("general-card")
        general_frame.setFrameShape(QFrame.StyledPanel)
        general_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        general_layout = QVBoxLayout(general_frame)
        
        # 卡片標題
        header_label = QLabel("一般設置")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        general_layout.addWidget(header_label)
        
        # 表單佈局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 系統名稱
        self.system_name_edit = QLineEdit()
        form_layout.addRow("系統名稱:", self.system_name_edit)
        
        # 默認語言
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文(繁體)", "English", "中文(简体)", "日本語"])
        form_layout.addRow("默認語言:", self.language_combo)
        
        # 時區
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([
            "Asia/Taipei (GMT+8)",
            "Asia/Hong Kong (GMT+8)",
            "Asia/Tokyo (GMT+9)",
            "America/Los Angeles (GMT-8)",
            "America/New York (GMT-5)"
        ])
        form_layout.addRow("時區:", self.timezone_combo)
        
        # 日期格式
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "YYYY-MM-DD",
            "DD-MM-YYYY",
            "MM-DD-YYYY",
            "YYYY/MM/DD"
        ])
        form_layout.addRow("日期格式:", self.date_format_combo)
        
        # 時間格式
        self.time_format_combo = QComboBox()
        self.time_format_combo.addItems(["24小時制", "12小時制"])
        form_layout.addRow("時間格式:", self.time_format_combo)
        
        # 默認存儲路徑
        storage_layout = QHBoxLayout()
        self.storage_path_edit = QLineEdit()
        browse_button = QPushButton("瀏覽")
        browse_button.clicked.connect(self.browse_storage_path)
        
        storage_layout.addWidget(self.storage_path_edit)
        storage_layout.addWidget(browse_button)
        
        form_layout.addRow("默認存儲路徑:", storage_layout)
        
        # 自動備份設置
        backup_layout = QVBoxLayout()
        
        backup_enable_layout = QHBoxLayout()
        self.backup_enable_checkbox = QCheckBox("啟用自動備份")
        backup_enable_layout.addWidget(self.backup_enable_checkbox)
        backup_enable_layout.addStretch()
        
        backup_layout.addLayout(backup_enable_layout)
        
        backup_settings_layout = QHBoxLayout()
        
        backup_frequency_layout = QFormLayout()
        self.backup_frequency_combo = QComboBox()
        self.backup_frequency_combo.addItems(["每日", "每週", "每月"])
        backup_frequency_layout.addRow("備份頻率:", self.backup_frequency_combo)
        
        backup_time_layout = QFormLayout()
        self.backup_time_edit = QTimeEdit()
        self.backup_time_edit.setTime(QTime(3, 0))  # 默認凌晨3點
        self.backup_time_edit.setDisplayFormat("HH:mm")
        backup_time_layout.addRow("備份時間:", self.backup_time_edit)
        
        backup_settings_layout.addLayout(backup_frequency_layout)
        backup_settings_layout.addLayout(backup_time_layout)
        
        backup_layout.addLayout(backup_settings_layout)
        
        form_layout.addRow("自動備份設置:", backup_layout)
        
        general_layout.addLayout(form_layout)
        
        # 保存按鈕
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("保存設置")
        save_button.setObjectName("btn-success")
        save_button.clicked.connect(self.save_general_settings)
        
        button_layout.addWidget(save_button)
        general_layout.addLayout(button_layout)
        
        layout.addWidget(general_frame)
    
    def setup_users_tab(self):
        """設置用戶管理標籤頁"""
        layout = QVBoxLayout(self.users_tab)
        
        # 用戶管理卡片
        users_frame = QFrame()
        users_frame.setObjectName("users-card")
        users_frame.setFrameShape(QFrame.StyledPanel)
        users_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        users_layout = QVBoxLayout(users_frame)
        
        # 卡片標題和添加按鈕
        header_layout = QHBoxLayout()
        
        header_label = QLabel("用戶管理")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        add_user_button = QPushButton("新增用戶")
        add_user_button.setIcon(QIcon("assets/icons/user-plus.ico"))
        add_user_button.clicked.connect(self.add_user)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(add_user_button)
        
        users_layout.addLayout(header_layout)
        
        # 搜索和過濾工具欄
        tools_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("搜尋用戶...")
        search_input.setClearButtonEnabled(True)
        
        role_combo = QComboBox()
        role_combo.addItems(["所有角色", "管理員", "會計", "分析師", "檢視者"])
        
        tools_layout.addWidget(search_input, 2)
        tools_layout.addWidget(role_combo, 1)
        
        users_layout.addLayout(tools_layout)
        
        # 用戶表格
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["用戶名", "姓名", "電子郵件", "角色", "狀態", "操作"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        users_layout.addWidget(self.users_table)
        layout.addWidget(users_frame)
    
    def setup_permissions_tab(self):
        """設置權限設置標籤頁"""
        layout = QVBoxLayout(self.permissions_tab)
        
        # 權限設置卡片
        permissions_frame = QFrame()
        permissions_frame.setObjectName("permissions-card")
        permissions_frame.setFrameShape(QFrame.StyledPanel)
        permissions_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        permissions_layout = QVBoxLayout(permissions_frame)
        
        # 卡片標題
        header_label = QLabel("權限設置")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        permissions_layout.addWidget(header_label)
        
        # 角色表格
        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(7)
        self.roles_table.setHorizontalHeaderLabels([
            "角色", "文件上傳", "文件管理", "處理配置", 
            "數據連接", "任務執行", "結果管理"
        ])
        self.roles_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.roles_table.verticalHeader().setVisible(False)
        
        # 添加角色行
        roles = ["管理員", "會計", "分析師", "檢視者"]
        self.roles_table.setRowCount(len(roles))
        
        for i, role in enumerate(roles):
            self.roles_table.setItem(i, 0, QTableWidgetItem(role))
            
            # 設置權限複選框
            for j in range(1, 7):
                checkbox = QCheckBox()
                checkbox.setChecked(True if role == "管理員" or (role == "會計" and j < 5) else False)
                self.roles_table.setCellWidget(i, j, self.create_centered_checkbox(checkbox))
        
        permissions_layout.addWidget(self.roles_table)
        
        # 保存按鈕
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("保存權限設置")
        save_button.setObjectName("btn-success")
        save_button.clicked.connect(self.save_permissions)
        
        button_layout.addWidget(save_button)
        permissions_layout.addLayout(button_layout)
        
        layout.addWidget(permissions_frame)
    
    def setup_logs_tab(self):
        """設置系統日誌標籤頁"""
        layout = QVBoxLayout(self.logs_tab)
        
        # 系統日誌卡片
        logs_frame = QFrame()
        logs_frame.setObjectName("logs-card")
        logs_frame.setFrameShape(QFrame.StyledPanel)
        logs_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        logs_layout = QVBoxLayout(logs_frame)
        
        # 卡片標題和過濾按鈕
        header_layout = QHBoxLayout()
        
        header_label = QLabel("系統日誌")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        level_combo = QComboBox()
        level_combo.addItems(["所有級別", "信息", "警告", "錯誤", "嚴重錯誤"])
        level_combo.currentIndexChanged.connect(self.filter_logs)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("日誌級別:"))
        header_layout.addWidget(level_combo)
        
        logs_layout.addLayout(header_layout)
        
        # 日誌表格
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(4)
        self.logs_table.setHorizontalHeaderLabels(["時間", "級別", "用戶", "訊息"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        logs_layout.addWidget(self.logs_table)
        
        # 分頁和清理按鈕
        footer_layout = QHBoxLayout()
        
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("頁碼:"))
        
        page_combo = QComboBox()
        page_combo.addItems(["1", "2", "3", "4", "5"])
        page_layout.addWidget(page_combo)
        
        page_layout.addWidget(QLabel("每頁顯示:"))
        
        rows_combo = QComboBox()
        rows_combo.addItems(["20", "50", "100"])
        page_layout.addWidget(rows_combo)
        
        clear_button = QPushButton("清除日誌")
        clear_button.setObjectName("btn-danger")
        clear_button.clicked.connect(self.clear_logs)
        
        export_button = QPushButton("導出日誌")
        export_button.clicked.connect(self.export_logs)
        
        footer_layout.addLayout(page_layout)
        footer_layout.addStretch()
        footer_layout.addWidget(export_button)
        footer_layout.addWidget(clear_button)
        
        logs_layout.addLayout(footer_layout)
        
        layout.addWidget(logs_frame)
    
    def create_centered_checkbox(self, checkbox):
        """創建居中的複選框"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(checkbox, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return container
    
    def load_settings(self):
        """載入系統設置"""
        # 從資料庫或配置文件載入設置
        # 這裡簡化處理，使用默認值
        
        # 一般設置
        self.system_name_edit.setText("會計底稿處理系統")
        self.language_combo.setCurrentIndex(0)  # 中文(繁體)
        self.timezone_combo.setCurrentIndex(0)  # Asia/Taipei
        self.date_format_combo.setCurrentIndex(0)  # YYYY-MM-DD
        self.time_format_combo.setCurrentIndex(0)  # 24小時制
        self.storage_path_edit.setText("/var/data/accounting")
        self.backup_enable_checkbox.setChecked(True)
        self.backup_frequency_combo.setCurrentIndex(0)  # 每日
        self.backup_time_edit.setTime(QTime(3, 0))  # 凌晨3點
        
        # 載入用戶列表
        self.load_users()
        
        # 載入系統日誌
        self.load_logs()
    
    def load_users(self):
        """載入用戶列表"""
        # 從資料庫獲取用戶
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, name, email, role, status
            FROM users
            ORDER BY id ASC
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        # 填充用戶表格
        self.users_table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(user[1]))
            self.users_table.setItem(i, 1, QTableWidgetItem(user[2]))
            self.users_table.setItem(i, 2, QTableWidgetItem(user[3] or ""))
            self.users_table.setItem(i, 3, QTableWidgetItem(user[4]))
            
            # 狀態單元格
            status_cell = QTableWidgetItem(user[5])
            if user[5] == '啟用':
                status_cell.setBackground(Qt.green)
            elif user[5] == '待啟用':
                status_cell.setBackground(Qt.yellow)
            else:
                status_cell.setBackground(Qt.gray)
            
            self.users_table.setItem(i, 4, status_cell)
            
            # 操作按鈕
            operations_widget = QWidget()
            operations_layout = QHBoxLayout(operations_widget)
            operations_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("編輯")
            edit_button.setProperty("user_id", user[0])
            edit_button.clicked.connect(lambda _, id=user[0]: self.edit_user(id))
            
            delete_button = QPushButton("刪除")
            delete_button.setProperty("user_id", user[0])
            delete_button.setObjectName("btn-danger")
            delete_button.clicked.connect(lambda _, id=user[0]: self.delete_user(id))
            
            operations_layout.addWidget(edit_button)
            operations_layout.addWidget(delete_button)
            
            self.users_table.setCellWidget(i, 5, operations_widget)
    
    def load_logs(self):
        """載入系統日誌"""
        # 從資料庫獲取日誌
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.id, l.level, l.message, l.created_at, u.username
            FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
            LIMIT 20
        """)
        
        logs = cursor.fetchall()
        conn.close()
        
        # 填充日誌表格
        self.logs_table.setRowCount(len(logs))
        
        for i, log in enumerate(logs):
            self.logs_table.setItem(i, 0, QTableWidgetItem(log[3]))
            
            # 日誌級別
            level_cell = QTableWidgetItem(log[1])
            if log[1] == 'error':
                level_cell.setText("錯誤")
                level_cell.setBackground(Qt.red)
            elif log[1] == 'warning':
                level_cell.setText("警告")
                level_cell.setBackground(Qt.yellow)
            elif log[1] == 'info':
                level_cell.setText("信息")
                level_cell.setBackground(Qt.green)
            else:
                level_cell.setText(log[1])
            
            self.logs_table.setItem(i, 1, level_cell)
            
            # 用戶和訊息
            self.logs_table.setItem(i, 2, QTableWidgetItem(log[4] or "系統"))
            self.logs_table.setItem(i, 3, QTableWidgetItem(log[2]))
    
    def browse_storage_path(self):
        """選擇存儲路徑"""
        directory = QFileDialog.getExistingDirectory(self, "選擇存儲路徑")
        if directory:
            self.storage_path_edit.setText(directory)
    
    def save_general_settings(self):
        """保存一般設置"""
        # 獲取設置值
        system_name = self.system_name_edit.text()
        language = self.language_combo.currentText()
        timezone = self.timezone_combo.currentText()
        date_format = self.date_format_combo.currentText()
        time_format = self.time_format_combo.currentText()
        storage_path = self.storage_path_edit.text()
        backup_enabled = self.backup_enable_checkbox.isChecked()
        backup_frequency = self.backup_frequency_combo.currentText()
        backup_time = self.backup_time_edit.time().toString("HH:mm")
        
        # 驗證設置
        if not system_name:
            QMessageBox.warning(self, "保存失敗", "系統名稱不能為空")
            return
        
        if not storage_path:
            QMessageBox.warning(self, "保存失敗", "存儲路徑不能為空")
            return
        
        # 保存設置到配置文件或資料庫
        # 這裡只是示例，實際應用中需要實現保存邏輯
        QMessageBox.information(self, "保存成功", "一般設置已成功保存")
    
    def add_user(self):
        """添加新用戶"""
        # 簡化處理，直接添加一個測試用戶
        new_user = {
            'username': f"user{self.users_table.rowCount() + 1}",
            'name': f"測試用戶 {self.users_table.rowCount() + 1}",
            'email': f"user{self.users_table.rowCount() + 1}@example.com",
            'role': "檢視者",
            'status': "待啟用",
            'password': "password"  # 實際應用中應加密處理
        }
        
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # 查詢用戶名是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ?", (new_user['username'],))
            if cursor.fetchone():
                QMessageBox.warning(self, "添加失敗", f"用戶名 '{new_user['username']}' 已存在")
                conn.close()
                return
            
            # 插入新用戶
            password_hash = db.hash_password(new_user['password'])
            
            cursor.execute("""
                INSERT INTO users (username, password, name, email, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                new_user['username'],
                password_hash,
                new_user['name'],
                new_user['email'],
                new_user['role'],
                new_user['status']
            ))
            
            conn.commit()
            
            # 重新載入用戶列表
            self.load_users()
            
            QMessageBox.information(self, "添加成功", f"已成功添加用戶 '{new_user['username']}'")
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "添加失敗", f"添加用戶時發生錯誤：{str(e)}")
            
        finally:
            conn.close()
    
    def edit_user(self, user_id):
        """編輯用戶"""
        # 在實際應用中，這裡應該顯示一個編輯用戶的對話框
        QMessageBox.information(self, "編輯用戶", f"正在編輯用戶ID: {user_id}")
    
    def delete_user(self, user_id):
        """刪除用戶"""
        confirm = QMessageBox.question(
            self, "確認刪除", "確定要刪除此用戶嗎？此操作無法撤銷。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            try:
                # 獲取用戶資訊
                cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    QMessageBox.warning(self, "刪除失敗", "未找到指定用戶")
                    conn.close()
                    return
                
                username = user[0]
                
                # 刪除用戶
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                
                # 重新載入用戶列表
                self.load_users()
                
                QMessageBox.information(self, "刪除成功", f"已成功刪除用戶 '{username}'")
                
            except Exception as e:
                conn.rollback()
                QMessageBox.critical(self, "刪除失敗", f"刪除用戶時發生錯誤：{str(e)}")
                
            finally:
                conn.close()
    
    def save_permissions(self):
        """保存權限設置"""
        # 獲取權限設置
        permissions = {}
        
        for i in range(self.roles_table.rowCount()):
            role = self.roles_table.item(i, 0).text()
            role_permissions = {}
            
            for j in range(1, 7):
                feature = self.roles_table.horizontalHeaderItem(j).text()
                checkbox = self.roles_table.cellWidget(i, j).findChild(QCheckBox)
                role_permissions[feature] = checkbox.isChecked()
            
            permissions[role] = role_permissions
        
        # 保存權限到配置文件或資料庫
        # 這裡只是示例，實際應用中需要實現保存邏輯
        QMessageBox.information(self, "保存成功", "權限設置已成功保存")
    
    def filter_logs(self, index):
        """根據級別過濾日誌"""
        level_filter = ["all", "info", "warning", "error", "critical"][index]
        
        # 重新載入日誌並應用過濾
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT l.id, l.level, l.message, l.created_at, u.username
            FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
        """
        params = []
        
        if level_filter != "all":
            query += " WHERE l.level = ?"
            params.append(level_filter)
        
        query += " ORDER BY l.created_at DESC LIMIT 20"
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()
        
        # 填充日誌表格
        self.logs_table.setRowCount(len(logs))
        
        for i, log in enumerate(logs):
            self.logs_table.setItem(i, 0, QTableWidgetItem(log[3]))
            
            # 日誌級別
            level_cell = QTableWidgetItem(log[1])
            if log[1] == 'error':
                level_cell.setText("錯誤")
                level_cell.setBackground(Qt.red)
            elif log[1] == 'warning':
                level_cell.setText("警告")
                level_cell.setBackground(Qt.yellow)
            elif log[1] == 'info':
                level_cell.setText("信息")
                level_cell.setBackground(Qt.green)
            else:
                level_cell.setText(log[1])
            
            self.logs_table.setItem(i, 1, level_cell)
            
            # 用戶和訊息
            self.logs_table.setItem(i, 2, QTableWidgetItem(log[4] or "系統"))
            self.logs_table.setItem(i, 3, QTableWidgetItem(log[2]))
    
    def clear_logs(self):
        """清除系統日誌"""
        confirm = QMessageBox.question(
            self, "確認清除", "確定要清除所有系統日誌嗎？此操作無法撤銷。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            try:
                # 清除日誌表
                cursor.execute("DELETE FROM system_logs")
                conn.commit()
                
                # 重新載入日誌列表
                self.load_logs()
                
                QMessageBox.information(self, "清除成功", "系統日誌已成功清除")
                
            except Exception as e:
                conn.rollback()
                QMessageBox.critical(self, "清除失敗", f"清除日誌時發生錯誤：{str(e)}")
                
            finally:
                conn.close()
    
    def export_logs(self):
        """導出系統日誌"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "導出日誌", "", "CSV檔案 (*.csv);;所有檔案 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # 從資料庫獲取所有日誌
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT l.id, l.level, l.message, l.created_at, u.username
                FROM system_logs l
                LEFT JOIN users u ON l.user_id = u.id
                ORDER BY l.created_at DESC
            """)
            
            logs = cursor.fetchall()
            conn.close()
            
            # 寫入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                
                # 寫入表頭
                writer.writerow(["ID", "時間", "級別", "用戶", "訊息"])
                
                # 寫入數據
                for log in logs:
                    writer.writerow([log[0], log[3], log[1], log[4] or "系統", log[2]])
            
            QMessageBox.information(self, "導出成功", f"系統日誌已成功導出到：{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "導出失敗", f"導出日誌時發生錯誤：{str(e)}")