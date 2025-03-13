import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTabWidget, QLineEdit, QPushButton,
                               QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
                               QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from utils.db import DatabaseManager

class ResultCard(QFrame):
    """結果卡片組件"""
    def __init__(self, result_data, parent=None):
        super().__init__(parent)
        self.result_data = result_data
        self.setObjectName("result-card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("border: 1px solid #eee; border-radius: 5px; padding: 15px; margin-bottom: 15px;")
        self.setup_ui()
    
    def setup_ui(self):
        """設置結果卡片UI"""
        layout = QHBoxLayout(self)
        
        # 結果圖標
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setStyleSheet("font-size: 24px;")
        
        # 設置圖標基於文件類型
        file_extension = self.result_data.get('extension', '').lower()
        if file_extension in ['.xlsx', '.xls']:
            icon_label.setText("📊")  # Excel圖標
        elif file_extension == '.csv':
            icon_label.setText("📋")  # CSV圖標
        elif file_extension == '.pdf':
            icon_label.setText("📄")  # PDF圖標
        else:
            icon_label.setText("📁")  # 默認文件圖標
        
        layout.addWidget(icon_label)
        
        # 結果內容
        content_layout = QVBoxLayout()
        
        # 結果標題
        title_label = QLabel(self.result_data['name'])
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        content_layout.addWidget(title_label)
        
        # 結果描述
        desc_label = QLabel(f"處理時間: {self.result_data['created_at']} | 文件大小: {self.result_data['size']}")
        desc_label.setStyleSheet("color: #95a5a6;")
        content_layout.addWidget(desc_label)
        
        # 操作按鈕
        buttons_layout = QHBoxLayout()
        
        preview_button = QPushButton("預覽")
        preview_button.setIcon(QIcon("assets/icons/eye.ico"))
        
        download_button = QPushButton("下載")
        download_button.setIcon(QIcon("assets/icons/download.ico"))
        
        share_button = QPushButton("分享")
        share_button.setIcon(QIcon("assets/icons/share.ico"))
        
        delete_button = QPushButton("刪除")
        delete_button.setIcon(QIcon("assets/icons/trash.ico"))
        delete_button.setObjectName("btn-danger")
        
        buttons_layout.addWidget(preview_button)
        buttons_layout.addWidget(download_button)
        buttons_layout.addWidget(share_button)
        buttons_layout.addWidget(delete_button)
        
        content_layout.addLayout(buttons_layout)
        layout.addLayout(content_layout)

class ResultManagementWidget(QWidget):
    """結果管理頁面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_results()
        
    def setup_ui(self):
        """設置結果管理UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("結果管理")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 結果列表卡片
        results_frame = QFrame()
        results_frame.setObjectName("results-card")
        results_frame.setFrameShape(QFrame.StyledPanel)
        results_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        results_layout = QVBoxLayout(results_frame)
        
        # 卡片標題
        header_label = QLabel("處理結果")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        results_layout.addWidget(header_label)
        
        # 標籤頁
        self.tab_widget = QTabWidget()
        
        # 最近結果標籤頁
        self.recent_tab = QWidget()
        recent_layout = QVBoxLayout(self.recent_tab)
        
        # 搜索和過濾工具欄
        tools_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("搜尋結果...")
        search_input.setClearButtonEnabled(True)
        
        category_combo = QComboBox()
        category_combo.addItems(["所有類型", "財務報表", "預算分析", "發票核對", "資產折舊"])
        
        tools_layout.addWidget(search_input, 2)
        tools_layout.addWidget(category_combo, 1)
        
        recent_layout.addLayout(tools_layout)
        
        # 結果卡片容器
        self.recent_content = QWidget()
        self.recent_content_layout = QVBoxLayout(self.recent_content)
        self.recent_content_layout.setAlignment(Qt.AlignTop)
        
        # 使用滾動區域包裝內容
        recent_scroll = QScrollArea()
        recent_scroll.setWidgetResizable(True)
        recent_scroll.setFrameShape(QFrame.NoFrame)
        recent_scroll.setWidget(self.recent_content)
        
        recent_layout.addWidget(recent_scroll)
        
        # 已歸檔標籤頁
        self.archived_tab = QWidget()
        archived_layout = QVBoxLayout(self.archived_tab)
        
        # 已歸檔結果卡片容器
        self.archived_content = QWidget()
        self.archived_content_layout = QVBoxLayout(self.archived_content)
        self.archived_content_layout.setAlignment(Qt.AlignTop)
        
        # 使用滾動區域包裝內容
        archived_scroll = QScrollArea()
        archived_scroll.setWidgetResizable(True)
        archived_scroll.setFrameShape(QFrame.NoFrame)
        archived_scroll.setWidget(self.archived_content)
        
        archived_layout.addWidget(archived_scroll)
        
        # 已共享標籤頁
        self.shared_tab = QWidget()
        shared_layout = QVBoxLayout(self.shared_tab)
        
        # 已共享結果卡片容器
        self.shared_content = QWidget()
        self.shared_content_layout = QVBoxLayout(self.shared_content)
        self.shared_content_layout.setAlignment(Qt.AlignTop)
        
        # 使用滾動區域包裝內容
        shared_scroll = QScrollArea()
        shared_scroll.setWidgetResizable(True)
        shared_scroll.setFrameShape(QFrame.NoFrame)
        shared_scroll.setWidget(self.shared_content)
        
        shared_layout.addWidget(shared_scroll)
        
        # 添加標籤頁
        self.tab_widget.addTab(self.recent_tab, "最近結果")
        self.tab_widget.addTab(self.archived_tab, "已歸檔")
        self.tab_widget.addTab(self.shared_tab, "已共享")
        
        results_layout.addWidget(self.tab_widget)
        layout.addWidget(results_frame)
        
        # 結果詳情卡片
        details_frame = QFrame()
        details_frame.setObjectName("details-card")
        details_frame.setFrameShape(QFrame.StyledPanel)
        details_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        details_layout = QVBoxLayout(details_frame)
        
        # 卡片標題
        details_header = QLabel("結果詳情")
        details_header.setStyleSheet("font-size: 18px; font-weight: bold;")
        details_layout.addWidget(details_header)
        
        # 結果詳情內容
        self.details_content = QLabel("選擇一個結果查看詳情")
        self.details_content.setAlignment(Qt.AlignCenter)
        self.details_content.setStyleSheet("color: #95a5a6; font-size: 16px; padding: 40px;")
        details_layout.addWidget(self.details_content)
        
        layout.addWidget(details_frame)
        
        # 連接信號
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
    def load_results(self, status_filter=None):
        """載入結果列表"""
        # 清空現有結果列表
        self.clear_layouts()
        
        # 從資料庫獲取結果
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 獲取所有結果
        query = """
            SELECT r.id, r.name, r.output_path, r.status, r.created_at,
                   t.name as task_name
            FROM results r
            LEFT JOIN tasks t ON r.task_id = t.id
        """
        params = []
        
        if status_filter:
            query += " WHERE r.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY r.created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # 按狀態分類結果
        recent_results = []
        archived_results = []
        shared_results = []
        
        for result in results:
            # 獲取文件大小
            file_size = "未知"
            try:
                file_path = result[2]
                if file_path and os.path.exists(file_path):
                    size_bytes = os.path.getsize(file_path)
                    if size_bytes < 1024:
                        file_size = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        file_size = f"{size_bytes / 1024:.1f} KB"
                    else:
                        file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
            except Exception as e:
                # 如果文件不存在或無法獲取大小
                print(e)
                pass
            
            # 構建結果數據
            result_data = {
                'id': result[0],
                'name': result[1],
                'path': result[2],
                'status': result[3],
                'created_at': result[4],
                'task_name': result[5],
                'size': file_size,
                'extension': os.path.splitext(result[2])[1] if result[2] else ''
            }
            
            # 按狀態添加到相應列表
            if result[3] == 'archived':
                archived_results.append(result_data)
            elif result[3] == 'shared':
                shared_results.append(result_data)
            else:
                recent_results.append(result_data)
        
        conn.close()
        
        # 添加結果卡片到相應標籤頁
        for result_data in recent_results:
            result_card = ResultCard(result_data)
            self.recent_content_layout.addWidget(result_card)
        
        for result_data in archived_results:
            result_card = ResultCard(result_data)
            self.archived_content_layout.addWidget(result_card)
        
        for result_data in shared_results:
            result_card = ResultCard(result_data)
            self.shared_content_layout.addWidget(result_card)
    
    def clear_layouts(self):
        """清空結果列表布局"""
        # 清空最近結果
        while self.recent_content_layout.count():
            item = self.recent_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 清空已歸檔結果
        while self.archived_content_layout.count():
            item = self.archived_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 清空已共享結果
        while self.shared_content_layout.count():
            item = self.shared_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def tab_changed(self, index):
        """標籤頁切換時調用"""
        # 根據標籤頁切換載入相應的結果
        if index == 0:  # 最近結果
            self.load_results()
        elif index == 1:  # 已歸檔
            self.load_results('archived')
        elif index == 2:  # 已共享
            self.load_results('shared')
    
    def show_result_details(self, result_id):
        """顯示結果詳情"""
        # 從資料庫獲取結果詳情
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.id, r.name, r.description, r.output_path, r.created_at,
                   t.name as task_name
            FROM results r
            LEFT JOIN tasks t ON r.task_id = t.id
            WHERE r.id = ?
        """, (result_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return
        
        # 更新詳情內容
        # 在實際應用中，這裡應該顯示更詳細的信息和可視化圖表
        self.details_content.setText(f"""
            <h3>{result[1]}</h3>
            <p>處理任務: {result[5] or '未知'}</p>
            <p>創建時間: {result[4]}</p>
            <p>描述: {result[2] or '無描述'}</p>
            <p>文件路徑: {result[3]}</p>
        """)
        self.details_content.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.details_content.setTextFormat(Qt.RichText)