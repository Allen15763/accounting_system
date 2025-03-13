from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTabWidget, QLineEdit, QPushButton,
                               QFormLayout, QComboBox, QCheckBox, QMessageBox,
                               QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from utils.db import DatabaseManager

class ConnectionCard(QFrame):
    """連接卡片組件"""
    def __init__(self, connection_data, parent=None):
        super().__init__(parent)
        self.connection_data = connection_data
        self.setObjectName("connection-card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("border: 1px solid #eee; border-radius: 5px; padding: 15px; margin-bottom: 15px;")
        self.setup_ui()
    
    def setup_ui(self):
        """設置連接卡片UI"""
        main_layout = QVBoxLayout(self)
        
        # 卡片標題和狀態
        header_layout = QHBoxLayout()
        
        # 連接狀態指示器
        status_indicator = QLabel()
        status_indicator.setFixedSize(10, 10)
        status_indicator.setStyleSheet(f"background-color: {'#27ae60' if self.connection_data['status'] == 'active' else '#e74c3c'}; border-radius: 5px;")
        
        # 連接標題
        title_label = QLabel(self.connection_data['name'])
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # 操作按鈕
        buttons_layout = QHBoxLayout()
        
        edit_button = QPushButton("編輯")
        edit_button.setProperty("connection_id", self.connection_data['id'])
        
        delete_button = QPushButton("刪除")
        delete_button.setProperty("connection_id", self.connection_data['id'])
        delete_button.setObjectName("btn-danger")
        
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        
        # 添加到標題布局
        header_layout.addWidget(status_indicator)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(buttons_layout)
        
        main_layout.addLayout(header_layout)
        
        # 連接詳情表單
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 連接名稱
        name_edit = QLineEdit(self.connection_data['name'])
        name_edit.setReadOnly(True)
        form_layout.addRow("連接名稱:", name_edit)
        
        # 連接類型
        type_edit = QLineEdit(self.connection_data['type'])
        type_edit.setReadOnly(True)
        form_layout.addRow("連接類型:", type_edit)
        
        # 服務器地址和端口
        server_port_layout = QHBoxLayout()
        
        server_edit = QLineEdit(self.connection_data['server'])
        server_edit.setReadOnly(True)
        
        port_edit = QLineEdit(self.connection_data['port'])
        port_edit.setReadOnly(True)
        
        server_port_layout.addWidget(server_edit)
        server_port_layout.addWidget(port_edit)
        
        form_layout.addRow("服務器地址/端口:", server_port_layout)
        
        # 根據連接類型添加額外字段
        if self.connection_data['type'] in ['MySQL', 'PostgreSQL', 'SQL Server']:
            # 數據庫名稱
            db_name_edit = QLineEdit(self.connection_data.get('database_name', ''))
            db_name_edit.setReadOnly(True)
            form_layout.addRow("數據庫名稱:", db_name_edit)
        
        # 用戶名和密碼
        user_pass_layout = QHBoxLayout()
        
        user_edit = QLineEdit(self.connection_data.get('username', ''))
        user_edit.setReadOnly(True)
        
        pass_edit = QLineEdit('********')
        pass_edit.setReadOnly(True)
        
        user_pass_layout.addWidget(user_edit)
        user_pass_layout.addWidget(pass_edit)
        
        form_layout.addRow("用戶名/密碼:", user_pass_layout)
        
        main_layout.addLayout(form_layout)
        
        # 測試連接按鈕
        test_button = QPushButton("測試連接")
        test_button.setObjectName("btn-success")
        test_button.setProperty("connection_id", self.connection_data['id'])
        
        main_layout.addWidget(test_button, alignment=Qt.AlignRight)

class DataConnectionWidget(QWidget):
    """數據連接頁面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_connections()
        
    def setup_ui(self):
        """設置數據連接UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("數據連接")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 連接管理卡片
        connections_frame = QFrame()
        connections_frame.setObjectName("connections-card")
        connections_frame.setFrameShape(QFrame.StyledPanel)
        connections_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        connections_layout = QVBoxLayout(connections_frame)
        
        # 卡片標題和新增按鈕
        header_layout = QHBoxLayout()
        header_label = QLabel("數據連接管理")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        add_connection_button = QPushButton("新增連接")
        add_connection_button.setIcon(QIcon("assets/icons/plus.ico"))
        add_connection_button.setCursor(Qt.PointingHandCursor)
        add_connection_button.clicked.connect(self.show_add_connection_dialog)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(add_connection_button)
        connections_layout.addLayout(header_layout)
        
        # 標籤頁
        self.tab_widget = QTabWidget()
        
        # OLAP連接標籤頁
        self.olap_tab = QWidget()
        olap_layout = QVBoxLayout(self.olap_tab)
        
        # 使用滾動區域包裝內容
        olap_scroll = QScrollArea()
        olap_scroll.setWidgetResizable(True)
        olap_scroll.setFrameShape(QFrame.NoFrame)
        
        # 創建內容小部件
        olap_content = QWidget()
        self.olap_content_layout = QVBoxLayout(olap_content)
        self.olap_content_layout.setAlignment(Qt.AlignTop)
        
        olap_scroll.setWidget(olap_content)
        olap_layout.addWidget(olap_scroll)
        
        # 數據庫連接標籤頁
        self.db_tab = QWidget()
        db_layout = QVBoxLayout(self.db_tab)
        
        # 使用滾動區域包裝內容
        db_scroll = QScrollArea()
        db_scroll.setWidgetResizable(True)
        db_scroll.setFrameShape(QFrame.NoFrame)
        
        # 創建內容小部件
        db_content = QWidget()
        self.db_content_layout = QVBoxLayout(db_content)
        self.db_content_layout.setAlignment(Qt.AlignTop)
        
        db_scroll.setWidget(db_content)
        db_layout.addWidget(db_scroll)
        
        # API連接標籤頁
        self.api_tab = QWidget()
        api_layout = QVBoxLayout(self.api_tab)
        
        # 使用滾動區域包裝內容
        api_scroll = QScrollArea()
        api_scroll.setWidgetResizable(True)
        api_scroll.setFrameShape(QFrame.NoFrame)
        
        # 創建內容小部件
        api_content = QWidget()
        self.api_content_layout = QVBoxLayout(api_content)
        self.api_content_layout.setAlignment(Qt.AlignTop)
        
        api_scroll.setWidget(api_content)
        api_layout.addWidget(api_scroll)
        
        # 添加標籤頁
        self.tab_widget.addTab(self.olap_tab, "OLAP 連接")
        self.tab_widget.addTab(self.db_tab, "數據庫連接")
        self.tab_widget.addTab(self.api_tab, "API 連接")
        
        connections_layout.addWidget(self.tab_widget)
        layout.addWidget(connections_frame)
    
    def load_connections(self):
        """載入連接列表"""
        # 清空現有連接列表
        self.clear_layouts()
        
        # 從資料庫獲取連接
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, type, server, port, database_name, username, status
            FROM connections
            ORDER BY name ASC
        """)
        
        connections = cursor.fetchall()
        conn.close()
        
        # 根據類型分類連接
        olap_connections = []
        db_connections = []
        api_connections = []
        
        for connection in connections:
            conn_data = {
                'id': connection[0],
                'name': connection[1],
                'type': connection[2],
                'server': connection[3],
                'port': connection[4],
                'database_name': connection[5],
                'username': connection[6],
                'status': connection[7]
            }
            
            if conn_data['type'] in ['OLAP', 'OLTP']:
                olap_connections.append(conn_data)
            elif conn_data['type'] in ['MySQL', 'PostgreSQL', 'SQL Server', 'Oracle', 'SQLite']:
                db_connections.append(conn_data)
            elif conn_data['type'] in ['REST API', 'SOAP API', 'GraphQL']:
                api_connections.append(conn_data)
        
        # 添加到相應的標籤頁
        for conn_data in olap_connections:
            conn_card = ConnectionCard(conn_data)
            self.olap_content_layout.addWidget(conn_card)
        
        for conn_data in db_connections:
            conn_card = ConnectionCard(conn_data)
            self.db_content_layout.addWidget(conn_card)
        
        for conn_data in api_connections:
            conn_card = ConnectionCard(conn_data)
            self.api_content_layout.addWidget(conn_card)
    
    def clear_layouts(self):
        """清空連接列表布局"""
        # 清空OLAP連接
        while self.olap_content_layout.count():
            item = self.olap_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 清空數據庫連接
        while self.db_content_layout.count():
            item = self.db_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 清空API連接
        while self.api_content_layout.count():
            item = self.api_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def show_add_connection_dialog(self):
        """顯示新增連接對話框"""
        # 這裡應該顯示一個對話框讓用戶輸入連接信息
        # 為了簡化示例，我們將直接創建一個連接
        
        # 在實際應用中，應彈出一個對話框讓用戶輸入資訊
        # 這裡只是一個簡化的演示，使用固定資訊
        
        new_connection = {
            'name': '新數據庫連接',
            'type': 'MySQL',
            'server': 'localhost',
            'port': '3306',
            'database_name': 'accounting_db',
            'username': 'user',
            'password': 'password',
            'status': 'inactive'
        }
        
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO connections (name, type, server, port, database_name, username, password, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_connection['name'],
                new_connection['type'],
                new_connection['server'],
                new_connection['port'],
                new_connection['database_name'],
                new_connection['username'],
                new_connection['password'],
                new_connection['status']
            ))
            
            conn.commit()
            
            # 重新載入連接列表
            self.load_connections()
            
            # 切換到適當的標籤頁
            if new_connection['type'] in ['OLAP', 'OLTP']:
                self.tab_widget.setCurrentIndex(0)
            elif new_connection['type'] in ['MySQL', 'PostgreSQL', 'SQL Server', 'Oracle', 'SQLite']:
                self.tab_widget.setCurrentIndex(1)
            elif new_connection['type'] in ['REST API', 'SOAP API', 'GraphQL']:
                self.tab_widget.setCurrentIndex(2)
            
            QMessageBox.information(self, "連接創建成功", "已成功創建新的數據連接")
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "連接創建失敗", f"創建連接時發生錯誤：{str(e)}")
        
        finally:
            conn.close()