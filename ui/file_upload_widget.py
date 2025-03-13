from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QLineEdit, QComboBox, QTextEdit, 
                               QPushButton, QFileDialog, QMessageBox, QCheckBox, QTableWidget, 
                               QTableWidgetItem, QHeaderView)

from PySide6.QtCore import Qt, QFile, QIODevice
from utils.db import DatabaseManager
import os
import shutil
import datetime

class FileUploadWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """設置文件上傳頁面UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("文件上傳")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 上傳卡片
        upload_frame = QFrame()
        upload_frame.setObjectName("upload-card")
        upload_frame.setFrameShape(QFrame.StyledPanel)
        upload_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        upload_layout = QVBoxLayout(upload_frame)
        
        upload_header = QLabel("上傳會計底稿文件")
        upload_header.setStyleSheet("font-size: 18px; font-weight: bold; padding-bottom: 10px;")
        upload_layout.addWidget(upload_header)
        
        # 上傳區域
        upload_area = QFrame()
        upload_area.setObjectName("upload-area")
        upload_area.setMinimumHeight(200)
        upload_area.setStyleSheet("border: 2px dashed #ddd; border-radius: 5px; padding: 20px;")
        upload_area_layout = QVBoxLayout(upload_area)
        
        upload_icon = QLabel("📂")
        upload_icon.setAlignment(Qt.AlignCenter)
        upload_icon.setStyleSheet("font-size: 48px; color: #3498db;")
        
        upload_text = QLabel("將文件拖放到此處或點擊上傳")
        upload_text.setAlignment(Qt.AlignCenter)
        upload_text.setStyleSheet("font-size: 16px; margin-top: 10px;")
        
        upload_desc = QLabel("支持格式: Excel (.xlsx, .xls), CSV (.csv), PDF (.pdf)")
        upload_desc.setAlignment(Qt.AlignCenter)
        upload_desc.setStyleSheet("color: #95a5a6; margin-top: 5px;")
        
        browse_button = QPushButton("選擇文件")
        browse_button.clicked.connect(self.browse_file)
        
        upload_area_layout.addWidget(upload_icon)
        upload_area_layout.addWidget(upload_text)
        upload_area_layout.addWidget(upload_desc)
        upload_area_layout.addWidget(browse_button, alignment=Qt.AlignCenter)
        
        upload_layout.addWidget(upload_area)
        
        # 文件信息表單
        form_layout = QVBoxLayout()
        
        # 文件名稱
        filename_layout = QHBoxLayout()
        filename_label = QLabel("文件名稱:")
        filename_label.setFixedWidth(100)
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("自動生成，可選擇修改")
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_edit)
        form_layout.addLayout(filename_layout)
        
        # 文件類別和處理類型
        category_type_layout = QHBoxLayout()
        
        category_label = QLabel("文件類別:")
        category_label.setFixedWidth(100)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["請選擇類別", "財務報表", "預算分析", "發票核對", "資產折舊", "其他"])
        
        process_label = QLabel("處理類型:")
        process_label.setFixedWidth(100)
        self.process_combo = QComboBox()
        self.process_combo.addItems(["請選擇處理類型", "標準處理", "預算分析", "發票匹配", "自定義處理"])
        
        category_layout = QHBoxLayout()
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        
        process_layout = QHBoxLayout()
        process_layout.addWidget(process_label)
        process_layout.addWidget(self.process_combo)
        
        category_type_layout.addLayout(category_layout)
        category_type_layout.addLayout(process_layout)
        form_layout.addLayout(category_type_layout)
        
        # 優先級
        priority_layout = QHBoxLayout()
        priority_label = QLabel("處理優先級:")
        priority_label.setFixedWidth(100)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["普通", "高", "緊急"])
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_combo)
        form_layout.addLayout(priority_layout)
        
        # 文件描述
        desc_layout = QHBoxLayout()
        desc_label = QLabel("文件描述:")
        desc_label.setFixedWidth(100)
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("輸入文件描述（可選）")
        self.desc_edit.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        form_layout.addLayout(desc_layout)
        
        # 上傳後處理選項
        process_option_layout = QHBoxLayout()
        self.process_checkbox = QCheckBox("上傳後立即處理")
        self.process_checkbox.setChecked(True)
        process_option_layout.addWidget(self.process_checkbox)
        process_option_layout.addStretch()
        form_layout.addLayout(process_option_layout)
        
        # 上傳按鈕
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.upload_button = QPushButton("上傳並處理")
        self.upload_button.setObjectName("btn-success")
        self.upload_button.clicked.connect(self.upload_file)
        self.upload_button.setEnabled(False)  # 禁用直到選擇文件
        button_layout.addWidget(self.upload_button)
        form_layout.addLayout(button_layout)
        
        upload_layout.addLayout(form_layout)
        layout.addWidget(upload_frame)
        
        # 上傳記錄區域
        records_frame = QFrame()
        records_frame.setObjectName("records-card")
        records_frame.setFrameShape(QFrame.StyledPanel)
        records_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        records_layout = QVBoxLayout(records_frame)
        
        records_header = QLabel("上傳記錄")
        records_header.setStyleSheet("font-size: 18px; font-weight: bold; padding-bottom: 10px;")
        records_layout.addWidget(records_header)
        
        # 上傳記錄表格
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels(["文件名", "類別", "上傳時間", "處理狀態", "操作"])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.verticalHeader().setVisible(False)
        self.records_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        records_layout.addWidget(self.records_table)
        layout.addWidget(records_frame)
        
        # 載入上傳記錄
        self.load_upload_records()
        
    def browse_file(self):
        """選擇文件對話框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇文件", "", 
            "Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;PDF文件 (*.pdf);;所有文件 (*.*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            file_name = os.path.basename(file_path)
            self.filename_edit.setText(file_name)
            self.upload_button.setEnabled(True)
            
            # 根據文件類型自動選擇類別
            extension = os.path.splitext(file_name)[1].lower()
            if extension in ['.xlsx', '.xls']:
                self.category_combo.setCurrentText("財務報表")
            elif extension == '.csv':
                self.category_combo.setCurrentText("預算分析")
            elif extension == '.pdf':
                self.category_combo.setCurrentText("其他")
    
    def upload_file(self):
        """上傳並處理文件"""
        if not self.selected_file_path:
            QMessageBox.warning(self, "上傳失敗", "請先選擇要上傳的文件")
            return
        
        file_name = self.filename_edit.text()
        category = self.category_combo.currentText()
        process_type = self.process_combo.currentText()
        priority = self.priority_combo.currentText()
        description = self.desc_edit.toPlainText()
        process_after_upload = self.process_checkbox.isChecked()
        
        if category == "請選擇類別":
            QMessageBox.warning(self, "上傳失敗", "請選擇文件類別")
            return
        
        if process_type == "請選擇處理類型":
            QMessageBox.warning(self, "上傳失敗", "請選擇處理類型")
            return
        
        try:
            # 創建目標目錄
            upload_dir = "data/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成唯一文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(self.selected_file_path)[1]
            unique_filename = f"{timestamp}_{file_name}"
            target_path = os.path.join(upload_dir, unique_filename)
            
            # 複製文件
            shutil.copy2(self.selected_file_path, target_path)
            
            # 儲存到資料庫
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            status = "pending"
            if process_after_upload:
                status = "processing"
            
            # 插入文件記錄
            cursor.execute("""
                INSERT INTO files (name, category, description, path, status)
                VALUES (?, ?, ?, ?, ?)
            """, (file_name, category, description, target_path, status))
            
            file_id = cursor.lastrowid
            
            # 如果需要立即處理，創建處理任務
            if process_after_upload:
                # 獲取處理配置ID
                cursor.execute("SELECT id FROM process_configs WHERE name = ?", (process_type,))
                config = cursor.fetchone()
                config_id = config[0] if config else None
                
                cursor.execute("""
                    INSERT INTO tasks (name, file_id, config_id, priority, status)
                    VALUES (?, ?, ?, ?, 'processing')
                """, (f"處理 {file_name}", file_id, config_id, priority))
            
            conn.commit()
            conn.close()
            
            # 更新UI
            self.selected_file_path = None
            self.filename_edit.clear()
            self.desc_edit.clear()
            self.category_combo.setCurrentIndex(0)
            self.process_combo.setCurrentIndex(0)
            self.priority_combo.setCurrentIndex(0)
            self.upload_button.setEnabled(False)
            
            # 重新載入上傳記錄
            self.load_upload_records()
            
            QMessageBox.information(self, "上傳成功", "文件已成功上傳")
            
        except Exception as e:
            QMessageBox.critical(self, "上傳失敗", f"上傳過程中發生錯誤：{str(e)}")
    
    def load_upload_records(self):
        """載入上傳記錄"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, created_at, status
            FROM files
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        records = cursor.fetchall()
        self.records_table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            self.records_table.setItem(row, 0, QTableWidgetItem(record[1]))
            self.records_table.setItem(row, 1, QTableWidgetItem(record[2]))
            self.records_table.setItem(row, 2, QTableWidgetItem(record[3]))
            
            # 狀態欄位
            status_cell = QTableWidgetItem(record[4])
            if record[4] == 'completed':
                status_cell.setBackground(Qt.green)
                status_cell.setText("已處理")
            elif record[4] == 'processing':
                status_cell.setBackground(Qt.yellow)
                status_cell.setText("處理中")
            elif record[4] == 'failed':
                status_cell.setBackground(Qt.red)
                status_cell.setText("處理失敗")
            else:
                status_cell.setText("未處理")
            
            self.records_table.setItem(row, 3, status_cell)
            
            # 操作按鈕
            # 這裡需要自定義小部件來支持按鈕功能
            # 暫時使用佔位符
            self.records_table.setItem(row, 4, QTableWidgetItem("查看/刪除"))
        
        conn.close()