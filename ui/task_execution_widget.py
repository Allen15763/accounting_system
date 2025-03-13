from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QProgressBar, QPushButton, QTabWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from utils.db import DatabaseManager

class TaskCard(QFrame):
    """任務卡片組件"""
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setObjectName("task-card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("border: 1px solid #eee; border-radius: 5px; padding: 15px; margin-bottom: 15px;")
        self.setup_ui()
    
    def setup_ui(self):
        """設置任務卡片UI"""
        layout = QVBoxLayout(self)
        
        # 任務標題和狀態
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.task_data['name'])
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        status_label = QLabel()
        if self.task_data['status'] == 'completed':
            status_label.setText("已完成")
            status_label.setStyleSheet("background-color: #27ae60; color: white; padding: 2px 8px; border-radius: 10px;")
        elif self.task_data['status'] == 'processing':
            status_label.setText("處理中")
            status_label.setStyleSheet("background-color: #f39c12; color: white; padding: 2px 8px; border-radius: 10px;")
        elif self.task_data['status'] == 'failed':
            status_label.setText("失敗")
            status_label.setStyleSheet("background-color: #e74c3c; color: white; padding: 2px 8px; border-radius: 10px;")
        elif self.task_data['status'] == 'pending':
            status_label.setText("等待中")
            status_label.setStyleSheet("background-color: #95a5a6; color: white; padding: 2px 8px; border-radius: 10px;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        
        layout.addLayout(header_layout)
        
        # 任務時間信息
        time_label = QLabel(f"開始時間: {self.task_data['started_at'] or 'N/A'} | 預計完成: {self.task_data['estimated_completion'] or 'N/A'}")
        time_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(time_label)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(self.task_data['progress']))
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 進度信息
        progress_layout = QHBoxLayout()
        
        progress_percent = QLabel(f"{int(self.task_data['progress'])}% 完成")
        
        steps_label = QLabel(f"處理步驟: {self.task_data['current_step']}/{self.task_data['total_steps']}")
        steps_label.setAlignment(Qt.AlignRight)
        
        progress_layout.addWidget(progress_percent)
        progress_layout.addStretch()
        progress_layout.addWidget(steps_label)
        
        layout.addLayout(progress_layout)
        
        # 操作按鈕
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        if self.task_data['status'] == 'processing':
            stop_button = QPushButton("停止")
            stop_button.setObjectName("btn-danger")
            stop_button.setProperty("task_id", self.task_data['id'])
            buttons_layout.addWidget(stop_button)
        
        if self.task_data['status'] == 'failed':
            retry_button = QPushButton("重試")
            retry_button.setObjectName("btn-warning")
            retry_button.setProperty("task_id", self.task_data['id'])
            buttons_layout.addWidget(retry_button)
        
        details_button = QPushButton("查看詳情")
        details_button.setProperty("task_id", self.task_data['id'])
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(details_button)
        
        layout.addLayout(buttons_layout)

class TaskExecutionWidget(QWidget):
    """任務執行頁面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_tasks()
        
        # 定時更新任務狀態
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_task_status)
        self.update_timer.start(5000)  # 每5秒更新一次
        
    def setup_ui(self):
        """設置任務執行UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("任務執行")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 任務列表卡片
        tasks_frame = QFrame()
        tasks_frame.setObjectName("tasks-card")
        tasks_frame.setFrameShape(QFrame.StyledPanel)
        tasks_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        tasks_layout = QVBoxLayout(tasks_frame)
        
        # 卡片標題和新增按鈕
        header_layout = QHBoxLayout()
        header_label = QLabel("任務列表")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        add_task_button = QPushButton("新增任務")
        add_task_button.setIcon(QIcon("assets/icons/plus.ico"))
        add_task_button.setCursor(Qt.PointingHandCursor)
        add_task_button.clicked.connect(self.show_add_task_dialog)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(add_task_button)
        tasks_layout.addLayout(header_layout)
        
        # 標籤頁
        self.tab_widget = QTabWidget()
        
        # 進行中標籤頁
        self.processing_tab = QWidget()
        processing_layout = QVBoxLayout(self.processing_tab)
        
        self.processing_content = QWidget()
        self.processing_content_layout = QVBoxLayout(self.processing_content)
        self.processing_content_layout.setAlignment(Qt.AlignTop)
        
        processing_layout.addWidget(self.processing_content)
        
        # 已完成標籤頁
        self.completed_tab = QWidget()
        completed_layout = QVBoxLayout(self.completed_tab)
        
        self.completed_content = QWidget()
        self.completed_content_layout = QVBoxLayout(self.completed_content)
        self.completed_content_layout.setAlignment(Qt.AlignTop)
        
        completed_layout.addWidget(self.completed_content)
        
        # 計劃中標籤頁
        self.pending_tab = QWidget()
        pending_layout = QVBoxLayout(self.pending_tab)
        
        self.pending_content = QWidget()
        self.pending_content_layout = QVBoxLayout(self.pending_content)
        self.pending_content_layout.setAlignment(Qt.AlignTop)
        
        pending_layout.addWidget(self.pending_content)
        
        # 失敗標籤頁
        self.failed_tab = QWidget()
        failed_layout = QVBoxLayout(self.failed_tab)
        
        self.failed_content = QWidget()
        self.failed_content_layout = QVBoxLayout(self.failed_content)
        self.failed_content_layout.setAlignment(Qt.AlignTop)
        
        failed_layout.addWidget(self.failed_content)
        
        # 添加標籤頁
        self.tab_widget.addTab(self.processing_tab, "進行中")
        self.tab_widget.addTab(self.completed_tab, "已完成")
        self.tab_widget.addTab(self.pending_tab, "計劃中")
        self.tab_widget.addTab(self.failed_tab, "失敗")
        
        tasks_layout.addWidget(self.tab_widget)
        layout.addWidget(tasks_frame)
        
        # 任務詳情卡片
        details_frame = QFrame()
        details_frame.setObjectName("details-card")
        details_frame.setFrameShape(QFrame.StyledPanel)
        details_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        details_layout = QVBoxLayout(details_frame)
        
        # 卡片標題
        details_header = QLabel("任務詳情")
        details_header.setStyleSheet("font-size: 18px; font-weight: bold;")
        details_layout.addWidget(details_header)
        
        # 任務詳情表單
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 任務名稱
        self.task_name_label = QLabel()
        form_layout.addRow("任務名稱:", self.task_name_label)
        
        # 處理配置
        self.task_config_label = QLabel()
        form_layout.addRow("處理配置:", self.task_config_label)
        
        # 任務優先級
        self.task_priority_label = QLabel()
        form_layout.addRow("任務優先級:", self.task_priority_label)
        
        # 開始和預計完成時間
        time_layout = QHBoxLayout()
        
        self.task_start_label = QLabel()
        self.task_end_label = QLabel()
        
        time_layout.addWidget(self.task_start_label)
        time_layout.addWidget(QLabel("|"))
        time_layout.addWidget(self.task_end_label)
        
        form_layout.addRow("時間:", time_layout)
        
        # 處理進度
        progress_layout = QVBoxLayout()
        
        self.task_progress_bar = QProgressBar()
        self.task_progress_bar.setRange(0, 100)
        self.task_progress_bar.setValue(0)
        
        self.task_progress_label = QLabel()
        
        progress_layout.addWidget(self.task_progress_bar)
        progress_layout.addWidget(self.task_progress_label)
        
        form_layout.addRow("處理進度:", progress_layout)
        
        # 處理步驟表格
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(4)
        self.steps_table.setHorizontalHeaderLabels(["步驟", "描述", "狀態", "用時"])
        self.steps_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.steps_table.verticalHeader().setVisible(False)
        self.steps_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        form_layout.addRow("處理步驟:", self.steps_table)
        
        details_layout.addLayout(form_layout)
        
        # 操作按鈕
        buttons_layout = QHBoxLayout()
        
        self.stop_task_button = QPushButton("停止任務")
        self.stop_task_button.setObjectName("btn-danger")
        self.stop_task_button.setVisible(False)
        
        self.refresh_button = QPushButton("刷新狀態")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.stop_task_button)
        buttons_layout.addWidget(self.refresh_button)
        
        details_layout.addLayout(buttons_layout)
        layout.addWidget(details_frame)
        
        # 連接信號
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.refresh_button.clicked.connect(self.refresh_task_details)
        
    def load_tasks(self):
        """載入任務列表"""
        # 清空所有任務列表
        self.clear_layouts()
        
        # 從資料庫獲取任務
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 獲取所有任務
        cursor.execute("""
            SELECT t.id, t.name, t.priority, t.status, t.progress, t.started_at, t.completed_at,
                   f.name as file_name, p.name as config_name
            FROM tasks t
            LEFT JOIN files f ON t.file_id = f.id
            LEFT JOIN process_configs p ON t.config_id = p.id
            ORDER BY 
                CASE 
                    WHEN t.status = 'processing' THEN 1
                    WHEN t.status = 'pending' THEN 2
                    WHEN t.status = 'failed' THEN 3
                    WHEN t.status = 'completed' THEN 4
                END,
                t.started_at DESC
        """)
        
        tasks = cursor.fetchall()
        
        # 按狀態分類任務
        processing_tasks = []
        completed_tasks = []
        pending_tasks = []
        failed_tasks = []
        
        for task in tasks:
            # 獲取任務步驟信息
            cursor.execute("""
                SELECT COUNT(*) FROM task_steps
                WHERE task_id = ?
            """, (task[0],))
            
            total_steps = cursor.fetchone()[0] or 4  # 默認4個步驟
            
            cursor.execute("""
                SELECT COUNT(*) FROM task_steps
                WHERE task_id = ? AND status = 'completed'
            """, (task[0],))
            
            completed_steps = cursor.fetchone()[0] or 0
            
            # 構建任務數據
            task_data = {
                'id': task[0],
                'name': task[1],
                'priority': task[2],
                'status': task[3],
                'progress': task[4] or 0,
                'started_at': task[5],
                'completed_at': task[6],
                'file_name': task[7],
                'config_name': task[8],
                'current_step': completed_steps + (1 if task[3] == 'processing' else 0),
                'total_steps': total_steps,
                'estimated_completion': self.estimate_completion_time(task[5], task[4], task[6])
            }
            
            # 按狀態添加到相應列表
            if task[3] == 'processing':
                processing_tasks.append(task_data)
            elif task[3] == 'completed':
                completed_tasks.append(task_data)
            elif task[3] == 'pending':
                pending_tasks.append(task_data)
            elif task[3] == 'failed':
                failed_tasks.append(task_data)
        
        conn.close()
        
        # 添加任務卡片到相應標籤頁
        for task_data in processing_tasks:
            task_card = TaskCard(task_data)
            task_card.clicked.connect(lambda _, id=task_data['id']: self.show_task_details(id))
            self.processing_content_layout.addWidget(task_card)
        
        for task_data in completed_tasks:
            task_card = TaskCard(task_data)
            task_card.clicked.connect(lambda _, id=task_data['id']: self.show_task_details(id))
            self.completed_content_layout.addWidget(task_card)
        
        for task_data in pending_tasks:
            task_card = TaskCard(task_data)
            task_card.clicked.connect(lambda _, id=task_data['id']: self.show_task_details(id))
            self.pending_content_layout.addWidget(task_card)
        
        for task_data in failed_tasks:
            task_card = TaskCard(task_data)
            task_card.clicked.connect(lambda _, id=task_data['id']: self.show_task_details(id))
            self.failed_content_layout.addWidget(task_card)
    
    def clear_layouts(self):
        """清空任務列表布局"""
        # 清空進行中任務
        while self.processing_content_layout.count():
            item = self.processing_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 清空已完成任務
        while self.completed_content_layout.count():
            item = self.completed_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 清空計劃中任務
        while self.pending_content_layout.count():
            item = self.pending_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 清空失敗任務
        while self.failed_content_layout.count():
            item = self.failed_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def tab_changed(self, index):
        """標籤頁切換時調用"""
        # 此方法可用於根據標籤頁切換來更新任務列表
        pass
    
    def show_task_details(self, task_id):
        """顯示任務詳情"""
        # 從資料庫獲取任務詳情
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.name, t.priority, t.status, t.progress, t.started_at, t.completed_at,
                   f.name as file_name, p.name as config_name
            FROM tasks t
            LEFT JOIN files f ON t.file_id = f.id
            LEFT JOIN process_configs p ON t.config_id = p.id
            WHERE t.id = ?
        """, (task_id,))
        
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return
        
        # 填充任務詳情
        self.current_task_id = task[0]
        self.task_name_label.setText(task[1])
        self.task_config_label.setText(task[8] or "未指定")
        self.task_priority_label.setText(task[2])
        
        self.task_start_label.setText(f"開始時間: {task[5] or 'N/A'}")
        self.task_end_label.setText(f"完成時間: {task[6] or 'N/A'}")
        
        self.task_progress_bar.setValue(int(task[4] or 0))
        
        # 計算預計剩餘時間
        estimated_completion = self.estimate_completion_time(task[5], task[4], task[6])
        progress_text = f"{int(task[4] or 0)}% 完成"
        
        if task[3] == 'processing' and estimated_completion:
            progress_text += f" | 預計剩餘時間: {estimated_completion}"
        
        self.task_progress_label.setText(progress_text)
        
        # 設置停止按鈕可見性
        self.stop_task_button.setVisible(task[3] == 'processing')
        
        # 獲取任務步驟
        cursor.execute("""
            SELECT id, order_num, name, description, status, duration
            FROM task_steps
            WHERE task_id = ?
            ORDER BY order_num
        """, (task_id,))
        
        steps = cursor.fetchall()
        conn.close()
        
        # 填充步驟表格
        self.steps_table.setRowCount(len(steps))
        
        for i, step in enumerate(steps):
            self.steps_table.setItem(i, 0, QTableWidgetItem(str(step[1])))
            self.steps_table.setItem(i, 1, QTableWidgetItem(step[2]))
            
            # 步驟狀態
            status_cell = QTableWidgetItem()
            if step[4] == 'completed':
                status_cell.setText("已完成")
                status_cell.setBackground(Qt.green)
            elif step[4] == 'processing':
                status_cell.setText("處理中")
                status_cell.setBackground(Qt.yellow)
            elif step[4] == 'failed':
                status_cell.setText("失敗")
                status_cell.setBackground(Qt.red)
            else:
                status_cell.setText("等待中")
            
            self.steps_table.setItem(i, 2, status_cell)
            
            # 用時
            duration = step[5] or "-"
            self.steps_table.setItem(i, 3, QTableWidgetItem(str(duration)))
    
    def estimate_completion_time(self, started_at, progress, completed_at):
        """估計任務完成時間"""
        if completed_at:
            return "已完成"
        
        if not started_at or progress is None or float(progress) <= 0:
            return "未知"
        
        # 這裡應該有更複雜的邏輯來估計完成時間
        # 簡化起見，我們返回一個固定值
        return "25分鐘"
    
    def refresh_task_details(self):
        """刷新任務詳情"""
        if hasattr(self, 'current_task_id'):
            self.show_task_details(self.current_task_id)
    
    def update_task_status(self):
        """定時更新任務狀態"""
        # 在實際應用中，這裡應該查詢資料庫獲取最新的任務狀態
        # 並更新UI
        if hasattr(self, 'current_task_id'):
            self.refresh_task_details()
    
    def show_add_task_dialog(self):
        """顯示新增任務對話框"""
        # 在實際應用中，應該顯示一個對話框讓用戶輸入任務信息
        # 這裡簡化處理，直接創建一個測試任務
        
        # 創建測試任務
        test_task = {
            'name': '測試任務',
            'file_id': 1,  # 假設有一個ID為1的文件
            'config_id': 1,  # 假設有一個ID為1的配置
            'priority': '普通',
            'status': 'pending'
        }
        
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO tasks (name, file_id, config_id, priority, status, progress)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (
                test_task['name'],
                test_task['file_id'],
                test_task['config_id'],
                test_task['priority'],
                test_task['status']
            ))
            
            task_id = cursor.lastrowid
            
            # 創建任務步驟
            steps = [
                ('數據提取', '從Excel文件中提取數據'),
                ('數據清洗', '清理數據，處理缺失值'),
                ('數據計算', '進行必要的計算和轉換'),
                ('結果生成', '生成處理結果')
            ]
            
            for i, (name, desc) in enumerate(steps, 1):
                cursor.execute("""
                    INSERT INTO task_steps (task_id, order_num, name, description, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (task_id, i, name, desc))
            
            conn.commit()
            
            # 重新載入任務列表
            self.load_tasks()
            
            # 切換到計劃中標籤頁
            self.tab_widget.setCurrentIndex(2)
            
            QMessageBox.information(self, "任務創建成功", "已成功創建新任務")
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "任務創建失敗", f"創建任務時發生錯誤：{str(e)}")
        
        finally:
            conn.close()