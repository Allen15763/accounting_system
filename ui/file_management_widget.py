from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QComboBox, QLineEdit, QGridLayout,
                               QProgressBar, QMenu)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from utils.db import DatabaseManager
import os

class FileCard(QFrame):
    """文件卡片組件"""
    def __init__(self, file_data, parent=None):
        super().__init__(parent)
        self.file_data = file_data
        self.setObjectName("file-card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("border: 1px solid #eee; border-radius: 5px; padding: 15px;")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 文件圖標
        icon_label = QLabel()
        icon_label.setObjectName("file-icon")
        icon_label.setStyleSheet("font-size: 32px; color: #3498db;")
        
        # 設置圖標基於文件類型
        file_extension = os.path.splitext(self.file_data['name'])[1].lower()
        if file_extension in ['.xlsx', '.xls']:
            icon_label.setText("📊")  # Excel圖標
        elif file_extension == '.csv':
            icon_label.setText("📋")  # CSV圖標
        elif file_extension == '.pdf':
            icon_label.setText("📄")  # PDF圖標
        else:
            icon_label.setText("📁")  # 默認文件圖標
        
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        
        # 文件名稱
        name_label = QLabel(self.file_data['name'])
        name_label.setObjectName("file-name")
        name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # 上傳時間和大小
        info_label = QLabel(f"上傳於: {self.file_data['created_at']}")
        info_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 類別信息
        category_label = QLabel(f"大小: {self.file_data['size']} | 類別: {self.file_data['category']}")
        category_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        category_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(category_label)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)
        
        # 設置進度條進度和顏色
        if self.file_data['status'] == 'completed':
            self.progress_bar.setValue(100)
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        elif self.file_data['status'] == 'processing':
            self.progress_bar.setValue(75)
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #f39c12; }")
        elif self.file_data['status'] == 'failed':
            self.progress_bar.setValue(30)
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #95a5a6; }")
        
        # 進度狀態
        progress_layout = QHBoxLayout()
        
        status_text = ""
        if self.file_data['status'] == 'completed':
            status_text = "處理完成"
        elif self.file_data['status'] == 'processing':
            status_text = "處理中"
        elif self.file_data['status'] == 'failed':
            status_text = "處理失敗"
        else:
            status_text = "未處理"
        
        status_label = QLabel(status_text)
        if self.file_data['status'] == 'failed':
            status_label.setStyleSheet("color: #e74c3c;")
        
        progress_percent = QLabel(f"{self.progress_bar.value()}%")
        progress_percent.setStyleSheet("color: #95a5a6; font-size: 12px;")
        
        progress_layout.addWidget(status_label)
        progress_layout.addStretch()
        progress_layout.addWidget(progress_percent)
        layout.addLayout(progress_layout)
        
        # 操作按鈕
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        # 創建按鈕並根據狀態啟用/禁用
        view_button = QPushButton("👁️")
        view_button.setToolTip("查看")
        view_button.setFixedSize(QSize(30, 30))
        view_button.setEnabled(self.file_data['status'] == 'completed')
        
        download_button = QPushButton("⬇️")
        download_button.setToolTip("下載")
        download_button.setFixedSize(QSize(30, 30))
        download_button.setEnabled(self.file_data['status'] == 'completed')
        
        retry_button = QPushButton("🔄")
        retry_button.setToolTip("重試")
        retry_button.setFixedSize(QSize(30, 30))
        retry_button.setVisible(self.file_data['status'] == 'failed')
        
        delete_button = QPushButton("🗑️")
        delete_button.setToolTip("刪除")
        delete_button.setFixedSize(QSize(30, 30))
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(view_button)
        buttons_layout.addWidget(download_button)
        if self.file_data['status'] == 'failed':
            buttons_layout.addWidget(retry_button)
        buttons_layout.addWidget(delete_button)
        
        layout.addLayout(buttons_layout)

class FileManagementWidget(QWidget):
    """文件管理頁面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_files()
        
    def setup_ui(self):
        """設置文件管理UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("文件管理")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 文件管理卡片
        files_frame = QFrame()
        files_frame.setObjectName("files-card")
        files_frame.setFrameShape(QFrame.StyledPanel)
        files_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        files_layout = QVBoxLayout(files_frame)
        
        # 卡片標題和上傳按鈕
        header_layout = QHBoxLayout()
        header_label = QLabel("文件管理")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        upload_button = QPushButton("上傳文件")
        upload_button.setIcon(QIcon("assets/icons/upload.ico"))
        upload_button.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(upload_button)
        files_layout.addLayout(header_layout)
        
        # 標籤頁切換
        tabs_layout = QHBoxLayout()
        
        tab_names = ["全部文件", "已處理", "處理中", "未處理", "處理失敗"]
        self.tab_buttons = []
        
        for i, name in enumerate(tab_names):
            tab_button = QPushButton(name)
            tab_button.setCheckable(True)
            tab_button.setCursor(Qt.PointingHandCursor)
            tab_button.setFlat(True)
            
            if i == 0:  # 默認選中第一個標籤
                tab_button.setChecked(True)
                tab_button.setStyleSheet("border-bottom: 2px solid #3498db; color: #3498db;")
            else:
                tab_button.setStyleSheet("border-bottom: 2px solid transparent;")
            
            tab_button.clicked.connect(lambda checked, btn=tab_button, index=i: self.switch_tab(btn, index))
            tabs_layout.addWidget(tab_button)
            self.tab_buttons.append(tab_button)
        
        tabs_layout.addStretch()
        files_layout.addLayout(tabs_layout)
        
        # 搜索和過濾工具欄
        tools_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("搜尋文件...")
        search_input.setClearButtonEnabled(True)
        
        category_combo = QComboBox()
        category_combo.addItems(["所有類別", "財務報表", "預算分析", "發票核對", "資產折舊"])
        
        sort_combo = QComboBox()
        sort_combo.addItems(["最新上傳", "最舊上傳", "名稱 (A-Z)", "名稱 (Z-A)"])
        
        tools_layout.addWidget(search_input, 2)
        tools_layout.addWidget(category_combo, 1)
        tools_layout.addWidget(sort_combo, 1)
        files_layout.addLayout(tools_layout)
        
        # 文件卡片網格
        self.files_grid = QGridLayout()
        self.files_grid.setSpacing(20)
        
        files_layout.addLayout(self.files_grid)
        layout.addWidget(files_frame)
        
    def switch_tab(self, button, index):
        """切換標籤頁"""
        for btn in self.tab_buttons:
            if btn == button:
                btn.setChecked(True)
                btn.setStyleSheet("border-bottom: 2px solid #3498db; color: #3498db;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet("border-bottom: 2px solid transparent;")
        
        # 根據標籤索引載入相應的文件
        status_filter = None
        if index == 1:
            status_filter = 'completed'
        elif index == 2:
            status_filter = 'processing'
        elif index == 3:
            status_filter = 'pending'
        elif index == 4:
            status_filter = 'failed'
        
        self.load_files(status_filter)
        
    def load_files(self, status_filter=None):
        """載入文件列表"""
        # 清空當前網格
        while self.files_grid.count():
            item = self.files_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 從資料庫獲取文件
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, category, path, status, created_at
            FROM files
        """
        params = []
        
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        files = cursor.fetchall()
        
        # 計算文件大小函數
        def get_file_size(file_path):
            try:
                size_bytes = os.path.getsize(file_path)
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            except Exception as e:
                return "Unknown"
        
        # 添加文件卡片到網格
        for i, file in enumerate(files):
            file_data = {
                'id': file[0],
                'name': file[1],
                'category': file[2],
                'path': file[3],
                'status': file[4],
                'created_at': file[5],
                'size': get_file_size(file[3])
            }
            
            file_card = FileCard(file_data)
            
            row = i // 3
            col = i % 3
            
            self.files_grid.addWidget(file_card, row, col)
        
        conn.close()