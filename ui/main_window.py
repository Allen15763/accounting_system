from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QStackedWidget, QLabel, QPushButton)
from PySide6.QtCore import Qt
from ui.dashboard_widget import DashboardWidget
from ui.file_upload_widget import FileUploadWidget
from ui.file_management_widget import FileManagementWidget
from ui.process_config_widget import ProcessConfigWidget
from ui.data_connection_widget import DataConnectionWidget
from ui.task_execution_widget import TaskExecutionWidget
from ui.result_management_widget import ResultManagementWidget
from ui.system_settings_widget import SystemSettingsWidget

class MainWindow(QMainWindow):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setup_ui()
        
    def setup_ui(self):
        """設置主視窗UI"""
        self.setWindowTitle("會計底稿處理系統")
        self.resize(1200, 800)
        
        # 創建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 側邊欄
        self.sidebar = self.create_sidebar()
        
        # 內容區域
        self.content_stack = QStackedWidget()
        
        # 創建並添加各頁面到堆疊
        self.dashboard_widget = DashboardWidget()
        self.file_upload_widget = FileUploadWidget()
        self.file_management_widget = FileManagementWidget()
        self.process_config_widget = ProcessConfigWidget()
        self.data_connection_widget = DataConnectionWidget()
        self.task_execution_widget = TaskExecutionWidget()
        self.result_management_widget = ResultManagementWidget()
        self.system_settings_widget = SystemSettingsWidget()
        
        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.file_upload_widget)
        self.content_stack.addWidget(self.file_management_widget)
        self.content_stack.addWidget(self.process_config_widget)
        self.content_stack.addWidget(self.data_connection_widget)
        self.content_stack.addWidget(self.task_execution_widget)
        self.content_stack.addWidget(self.result_management_widget)
        self.content_stack.addWidget(self.system_settings_widget)
        
        # 添加到主佈局
        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.content_stack, 4)
        
        # 默認顯示儀表板
        self.content_stack.setCurrentIndex(0)
    
    def create_sidebar(self):
        """創建側邊欄"""
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setMinimumWidth(250)
        sidebar_widget.setMaximumWidth(250)
        
        # 側邊欄佈局
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # 標題區域
        title_widget = QWidget()
        title_widget.setObjectName("sidebar-title")
        title_layout = QVBoxLayout(title_widget)
        
        logo_label = QLabel("會計底稿處理系統")
        logo_label.setObjectName("sidebar-logo")
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(logo_label)
        sidebar_layout.addWidget(title_widget)
        
        # 創建功能選單按鈕
        menu_items = [
            {"icon": "tachometer-alt", "text": "儀表板", "index": 0},
            {"icon": "upload", "text": "文件上傳", "index": 1},
            {"icon": "folder", "text": "文件管理", "index": 2},
            {"icon": "cogs", "text": "處理配置", "index": 3},
            {"icon": "database", "text": "數據連接", "index": 4},
            {"icon": "play-circle", "text": "任務執行", "index": 5},
            {"icon": "chart-bar", "text": "結果管理", "index": 6},
            {"icon": "cog", "text": "系統設置", "index": 7},
            {"icon": "sign-out-alt", "text": "登出", "index": -1}
        ]
        
        # 添加選單按鈕
        for item in menu_items:
            button = QPushButton(item["text"])
            button.setObjectName("sidebar-button")
            if item["index"] == 0:  # 默認選中儀表板
                button.setProperty("active", True)
            
            # 設置圖示和功能
            if item["index"] >= 0:
                button.clicked.connect(lambda _, idx=item["index"]: self.switch_page(idx))
            else:  # 登出按鈕
                button.clicked.connect(self.logout)
            
            sidebar_layout.addWidget(button)
        
        # 添加下方空白區域
        sidebar_layout.addStretch()
        
        # 用戶信息區域
        user_widget = QWidget()
        user_widget.setObjectName("user-info")
        user_layout = QHBoxLayout(user_widget)
        
        avatar_label = QLabel("AL")
        avatar_label.setObjectName("user-avatar")
        
        user_details = QWidget()
        user_details_layout = QVBoxLayout(user_details)
        user_details_layout.setContentsMargins(5, 0, 0, 0)
        user_details_layout.setSpacing(0)
        
        name_label = QLabel(self.user_data["name"])
        name_label.setObjectName("user-name")
        
        role_label = QLabel(self.user_data["role"])
        role_label.setObjectName("user-role")
        
        user_details_layout.addWidget(name_label)
        user_details_layout.addWidget(role_label)
        
        user_layout.addWidget(avatar_label)
        user_layout.addWidget(user_details)
        
        sidebar_layout.addWidget(user_widget)
        
        return sidebar_widget
    
    def switch_page(self, index):
        """切換內容頁面"""
        # 更新側邊欄選中狀態
        for i in range(self.sidebar.layout().count() - 2):  # 排除拉伸和用戶信息
            button = self.sidebar.layout().itemAt(i+1).widget()
            if isinstance(button, QPushButton):
                button.setProperty("active", i == index)
                button.style().unpolish(button)
                button.style().polish(button)
        
        # 切換頁面
        self.content_stack.setCurrentIndex(index)
    
    def logout(self):
        """登出功能"""
        # 在實際應用中可能需要清理資源或狀態
        self.close()
        # 如需重新登入，可以在此啟動新的登入對話框