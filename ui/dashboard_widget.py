from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from utils.db import DatabaseManager

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """設置儀表板UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("儀表板")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 統計卡片區域
        stat_cards_layout = QHBoxLayout()
        stat_cards_layout.setSpacing(20)
        
        # 創建統計卡片
        stat_cards = [
            {"title": "總文件數", "value": "0", "color": "#3498db", "icon": "file-alt"},
            {"title": "已處理文件", "value": "0", "color": "#27ae60", "icon": "check-circle"},
            {"title": "處理中文件", "value": "0", "color": "#f39c12", "icon": "spinner"},
            {"title": "處理失敗文件", "value": "0", "color": "#e74c3c", "icon": "exclamation-circle"}
        ]
        
        for card in stat_cards:
            card_frame = QFrame()
            card_frame.setObjectName("stat-card")
            card_frame.setFrameShape(QFrame.StyledPanel)
            card_frame.setStyleSheet("background-color: white; border-radius: 5px;")
            
            card_layout = QHBoxLayout(card_frame)
            
            # 圖標區域
            icon_frame = QFrame()
            icon_frame.setFixedSize(60, 60)
            icon_frame.setStyleSheet(f"background-color: {card['color']}; border-radius: 10px;")
            icon_layout = QVBoxLayout(icon_frame)
            
            icon_label = QLabel()
            icon_label.setStyleSheet("color: white; font-size: 24px;")
            icon_layout.addWidget(icon_label, alignment=Qt.AlignCenter)
            
            # 內容區域
            content_layout = QVBoxLayout()
            
            value_label = QLabel(card["value"])
            value_label.setObjectName(f"stat-value-{card['title']}")
            value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            
            title_label = QLabel(card["title"])
            title_label.setStyleSheet("color: #95a5a6;")
            
            content_layout.addWidget(value_label)
            content_layout.addWidget(title_label)
            
            card_layout.addWidget(icon_frame)
            card_layout.addLayout(content_layout)
            
            stat_cards_layout.addWidget(card_frame)
        
        layout.addLayout(stat_cards_layout)
        
        # 最近處理任務區域
        tasks_frame = QFrame()
        tasks_frame.setObjectName("tasks-card")
        tasks_frame.setFrameShape(QFrame.StyledPanel)
        tasks_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        tasks_layout = QVBoxLayout(tasks_frame)
        
        tasks_header = QLabel("最近處理任務")
        tasks_header.setStyleSheet("font-size: 18px; font-weight: bold; padding-bottom: 10px;")
        tasks_layout.addWidget(tasks_header)
        
        # 創建表格
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(5)
        self.tasks_table.setHorizontalHeaderLabels(["文件名", "處理類型", "上傳時間", "狀態", "操作"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.verticalHeader().setVisible(False)
        self.tasks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        tasks_layout.addWidget(self.tasks_table)
        layout.addWidget(tasks_frame)
        
        # 最近活動區域
        activity_frame = QFrame()
        activity_frame.setObjectName("activity-card")
        activity_frame.setFrameShape(QFrame.StyledPanel)
        activity_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_header = QLabel("最近活動")
        activity_header.setStyleSheet("font-size: 18px; font-weight: bold; padding-bottom: 10px;")
        activity_layout.addWidget(activity_header)
        
        # 這裡將添加活動列表元素
        # 先使用占位元素
        for i in range(4):
            activity_item = QFrame()
            item_layout = QHBoxLayout(activity_item)
            
            # 活動圖標
            icon_label = QLabel()
            icon_label.setFixedSize(40, 40)
            icon_label.setStyleSheet("background-color: #3498db; color: white; border-radius: 20px;")
            
            # 活動內容
            content_layout = QVBoxLayout()
            title_label = QLabel(f"活動標題 {i+1}")
            title_label.setStyleSheet("font-weight: bold;")
            desc_label = QLabel("活動描述內容...")
            desc_label.setStyleSheet("color: #95a5a6;")
            content_layout.addWidget(title_label)
            content_layout.addWidget(desc_label)
            
            # 活動時間
            time_label = QLabel("10分鐘前")
            time_label.setStyleSheet("color: #95a5a6;")
            
            item_layout.addWidget(icon_label)
            item_layout.addLayout(content_layout, 1)
            item_layout.addWidget(time_label)
            
            activity_layout.addWidget(activity_item)
            
            # 如果不是最後一個項目，添加分隔線
            if i < 3:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setStyleSheet("background-color: #eee;")
                activity_layout.addWidget(line)
        
        layout.addWidget(activity_frame)
        
    def load_data(self):
        """從資料庫載入儀表板數據"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 載入文件統計
        cursor.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM files WHERE status = 'completed'")
        completed_files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM files WHERE status = 'processing'")
        processing_files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM files WHERE status = 'failed'")
        failed_files = cursor.fetchone()[0]
        
        # 更新統計卡片
        self.findChild(QLabel, "stat-value-總文件數").setText(str(total_files))
        self.findChild(QLabel, "stat-value-已處理文件").setText(str(completed_files))
        self.findChild(QLabel, "stat-value-處理中文件").setText(str(processing_files))
        self.findChild(QLabel, "stat-value-處理失敗文件").setText(str(failed_files))
        
        # 載入最近任務
        cursor.execute("""
            SELECT f.name, p.name, f.created_at, f.status
            FROM files f
            LEFT JOIN tasks t ON f.id = t.file_id
            LEFT JOIN process_configs p ON t.config_id = p.id
            ORDER BY f.created_at DESC
            LIMIT 10
        """)
        
        tasks = cursor.fetchall()
        self.tasks_table.setRowCount(len(tasks))
        
        # 填充任務表
        for row, task in enumerate(tasks):
            self.tasks_table.setItem(row, 0, QTableWidgetItem(task[0]))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task[1] or "未指定"))
            self.tasks_table.setItem(row, 2, QTableWidgetItem(task[2]))
            
            # 創建狀態標籤
            status_cell = QTableWidgetItem(task[3])
            if task[3] == 'completed':
                status_cell.setBackground(Qt.green)
            elif task[3] == 'processing':
                status_cell.setBackground(Qt.yellow)
            elif task[3] == 'failed':
                status_cell.setBackground(Qt.red)
            
            self.tasks_table.setItem(row, 3, status_cell)
            
            # 創建操作按鈕 (這裡需要自定義一個更複雜的小部件)
            # 暫時使用佔位符
            self.tasks_table.setItem(row, 4, QTableWidgetItem("查看/下載"))
        
        conn.close()