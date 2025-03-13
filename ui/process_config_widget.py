from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QComboBox, QLineEdit, QTextEdit,
                               QListWidget, QListWidgetItem, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from utils.db import DatabaseManager
import json

class ProcessConfigWidget(QWidget):
    """處理配置頁面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_configs()
        
    def setup_ui(self):
        """設置處理配置UI"""
        # 主佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel("處理配置")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 配置列表卡片
        configs_frame = QFrame()
        configs_frame.setObjectName("configs-card")
        configs_frame.setFrameShape(QFrame.StyledPanel)
        configs_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        configs_layout = QVBoxLayout(configs_frame)
        
        # 卡片標題和新增按鈕
        header_layout = QHBoxLayout()
        header_label = QLabel("處理規則配置")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        add_config_button = QPushButton("新增配置")
        add_config_button.setIcon(QIcon("assets/icons/plus.ico"))
        add_config_button.setCursor(Qt.PointingHandCursor)
        add_config_button.clicked.connect(self.show_add_config_dialog)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(add_config_button)
        configs_layout.addLayout(header_layout)
        
        # 標籤頁切換
        tabs_layout = QHBoxLayout()
        
        tab_names = ["預設配置", "自定義配置", "已歸檔配置"]
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
        configs_layout.addLayout(tabs_layout)
        
        # 配置表格
        self.configs_table = QTableWidget()
        self.configs_table.setColumnCount(6)
        self.configs_table.setHorizontalHeaderLabels(["配置名稱", "適用文件類型", "創建時間", "最後更新", "狀態", "操作"])
        self.configs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.configs_table.verticalHeader().setVisible(False)
        self.configs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.configs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.configs_table.setSelectionMode(QTableWidget.SingleSelection)
        
        configs_layout.addWidget(self.configs_table)
        layout.addWidget(configs_frame)
        
        # 配置詳情卡片
        details_frame = QFrame()
        details_frame.setObjectName("details-card")
        details_frame.setFrameShape(QFrame.StyledPanel)
        details_frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 15px;")
        details_layout = QVBoxLayout(details_frame)
        
        # 卡片標題
        details_header = QLabel("配置詳情")
        details_header.setStyleSheet("font-size: 18px; font-weight: bold;")
        details_layout.addWidget(details_header)
        
        # 配置詳情表單
        form_layout = QVBoxLayout()
        
        # 配置名稱
        name_layout = QHBoxLayout()
        name_label = QLabel("配置名稱:")
        name_label.setFixedWidth(100)
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        # 適用文件類型和狀態
        type_status_layout = QHBoxLayout()
        
        type_label = QLabel("適用文件類型:")
        type_label.setFixedWidth(100)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["所有類型", "Excel", "CSV", "PDF"])
        
        status_label = QLabel("狀態:")
        status_label.setFixedWidth(100)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["啟用", "測試中", "禁用"])
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_combo)
        
        type_status_layout.addLayout(type_layout)
        type_status_layout.addLayout(status_layout)
        form_layout.addLayout(type_status_layout)
        
        # 配置描述
        desc_layout = QHBoxLayout()
        desc_label = QLabel("配置描述:")
        desc_label.setFixedWidth(100)
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(70)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        form_layout.addLayout(desc_layout)
        
        # 處理步驟
        steps_label = QLabel("處理步驟:")
        form_layout.addWidget(steps_label)
        
        self.steps_list = QListWidget()
        self.steps_list.setMaximumHeight(200)
        form_layout.addWidget(self.steps_list)
        
        add_step_button = QPushButton("添加步驟")
        add_step_button.clicked.connect(self.add_step)
        form_layout.addWidget(add_step_button, alignment=Qt.AlignLeft)
        
        # 自定義處理腳本
        script_label = QLabel("自定義處理腳本:")
        form_layout.addWidget(script_label)
        
        self.script_edit = QTextEdit()
        self.script_edit.setPlaceholderText("# 在這裡輸入Python處理腳本")
        self.script_edit.setStyleSheet("font-family: monospace;")
        form_layout.addWidget(self.script_edit)
        
        # 保存按鈕
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.clear_form)
        
        save_button = QPushButton("儲存配置")
        save_button.setObjectName("btn-success")
        save_button.clicked.connect(self.save_config)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        form_layout.addLayout(button_layout)
        
        details_layout.addLayout(form_layout)
        layout.addWidget(details_frame)
        
        # 配置表格行選擇事件
        self.configs_table.cellClicked.connect(self.select_config)
        
    def switch_tab(self, button, index):
        """切換標籤頁"""
        for btn in self.tab_buttons:
            if btn == button:
                btn.setChecked(True)
                btn.setStyleSheet("border-bottom: 2px solid #3498db; color: #3498db;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet("border-bottom: 2px solid transparent;")
        
        # 根據標籤索引載入相應的配置
        type_filter = None
        if index == 0:
            type_filter = 'default'
        elif index == 1:
            type_filter = 'custom'
        elif index == 2:
            type_filter = 'archived'
        
        self.load_configs(type_filter)
        
    def load_configs(self, type_filter=None):
        """載入配置列表"""
        # 清空表格
        self.configs_table.setRowCount(0)
        
        # 從資料庫獲取配置
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, file_type, created_at, updated_at, status
            FROM process_configs
        """
        params = []
        
        if type_filter:
            if type_filter == 'archived':
                query += " WHERE status = 'archived'"
            elif type_filter == 'default':
                query += " WHERE is_default = 1"
            elif type_filter == 'custom':
                query += " WHERE is_default = 0 AND status != 'archived'"
        
        query += " ORDER BY updated_at DESC"
        
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        # 添加配置到表格
        for i, config in enumerate(configs):
            self.configs_table.insertRow(i)
            
            self.configs_table.setItem(i, 0, QTableWidgetItem(config[1]))
            self.configs_table.setItem(i, 1, QTableWidgetItem(config[2] or "所有類型"))
            self.configs_table.setItem(i, 2, QTableWidgetItem(config[3]))
            self.configs_table.setItem(i, 3, QTableWidgetItem(config[4]))
            
            # 狀態單元格
            status_cell = QTableWidgetItem(config[5])
            if config[5] == 'enabled':
                status_cell.setText("啟用")
                status_cell.setBackground(Qt.green)
            elif config[5] == 'testing':
                status_cell.setText("測試中")
                status_cell.setBackground(Qt.yellow)
            elif config[5] == 'disabled':
                status_cell.setText("禁用")
                status_cell.setBackground(Qt.gray)
            elif config[5] == 'archived':
                status_cell.setText("已歸檔")
                status_cell.setBackground(Qt.lightGray)
            
            self.configs_table.setItem(i, 4, status_cell)
            
            # 操作按鈕
            operations_cell = QTableWidgetItem()
            self.configs_table.setItem(i, 5, operations_cell)
            
            # 使用自定義小部件添加操作按鈕
            operations_widget = QWidget()
            operations_layout = QHBoxLayout(operations_widget)
            operations_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("編輯")
            edit_button.setProperty("config_id", config[0])
            edit_button.clicked.connect(lambda _, id=config[0]: self.edit_config(id))
            
            copy_button = QPushButton("複製")
            copy_button.setProperty("config_id", config[0])
            copy_button.clicked.connect(lambda _, id=config[0]: self.copy_config(id))
            
            operations_layout.addWidget(edit_button)
            operations_layout.addWidget(copy_button)
            
            self.configs_table.setCellWidget(i, 5, operations_widget)
        
        conn.close()
        
    def select_config(self, row, column):
        """選擇配置行"""
        config_name = self.configs_table.item(row, 0).text()
        
        # 從資料庫獲取完整配置資訊
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, file_type, description, configuration, status
            FROM process_configs
            WHERE name = ?
        """, (config_name,))
        
        config = cursor.fetchone()
        conn.close()
        
        if not config:
            return
        
        # 填充詳情表單
        self.current_config_id = config[0]
        self.name_edit.setText(config[1])
        
        # 設置適用文件類型
        file_type_index = 0  # 默認"所有類型"
        if config[2] == "Excel":
            file_type_index = 1
        elif config[2] == "CSV":
            file_type_index = 2
        elif config[2] == "PDF":
            file_type_index = 3
        self.type_combo.setCurrentIndex(file_type_index)
        
        # 設置狀態
        status_index = 0  # 默認"啟用"
        if config[5] == "testing":
            status_index = 1
        elif config[5] == "disabled":
            status_index = 2
        self.status_combo.setCurrentIndex(status_index)
        
        # 設置描述
        self.desc_edit.setText(config[3] or "")
        
        # 清空步驟列表
        self.steps_list.clear()
        
        # 解析配置JSON並填充步驟列表
        if config[4]:
            try:
                config_data = json.loads(config[4])
                
                # 填充處理步驟
                if 'steps' in config_data:
                    for step in config_data['steps']:
                        step_item = QListWidgetItem(f"{step['order']}. {step['name']}")
                        step_item.setData(Qt.UserRole, step)
                        self.steps_list.addItem(step_item)
                
                # 填充腳本
                if 'script' in config_data:
                    self.script_edit.setText(config_data['script'])
                else:
                    self.script_edit.clear()
            except Exception as e:
                print(str(e))
                self.script_edit.clear()
        else:
            self.script_edit.clear()
    
    def show_add_config_dialog(self):
        """顯示新增配置對話框"""
        # 清空表單以創建新配置
        self.current_config_id = None
        self.clear_form()
    
    def clear_form(self):
        """清空表單"""
        self.current_config_id = None
        self.name_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.desc_edit.clear()
        self.steps_list.clear()
        self.script_edit.clear()
    
    def add_step(self):
        """添加處理步驟"""
        # 獲取當前步驟數量
        steps_count = self.steps_list.count()
        
        # 創建新步驟
        new_step = {
            'order': steps_count + 1,
            'name': f"步驟 {steps_count + 1}",
            'description': "新步驟描述",
            'function': ""
        }
        
        # 添加到列表
        step_item = QListWidgetItem(f"{new_step['order']}. {new_step['name']}")
        step_item.setData(Qt.UserRole, new_step)
        self.steps_list.addItem(step_item)
    
    def edit_config(self, config_id):
        """編輯配置"""
        # 從資料庫載入配置詳情
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, file_type, description, configuration, status
            FROM process_configs
            WHERE id = ?
        """, (config_id,))
        
        config = cursor.fetchone()
        conn.close()
        
        if not config:
            return
        
        # 和選擇配置邏輯相同，填充詳情表單
        self.current_config_id = config[0]
        self.name_edit.setText(config[1])
        
        # 設置適用文件類型
        file_type_index = 0  # 默認"所有類型"
        if config[2] == "Excel":
            file_type_index = 1
        elif config[2] == "CSV":
            file_type_index = 2
        elif config[2] == "PDF":
            file_type_index = 3
        self.type_combo.setCurrentIndex(file_type_index)
        
        # 設置狀態
        status_index = 0  # 默認"啟用"
        if config[5] == "testing":
            status_index = 1
        elif config[5] == "disabled":
            status_index = 2
        self.status_combo.setCurrentIndex(status_index)
        
        # 設置描述
        self.desc_edit.setText(config[3] or "")
        
        # 清空步驟列表
        self.steps_list.clear()
        
        # 解析配置JSON並填充步驟列表
        if config[4]:
            try:
                config_data = json.loads(config[4])
                
                # 填充處理步驟
                if 'steps' in config_data:
                    for step in config_data['steps']:
                        step_item = QListWidgetItem(f"{step['order']}. {step['name']}")
                        step_item.setData(Qt.UserRole, step)
                        self.steps_list.addItem(step_item)
                
                # 填充腳本
                if 'script' in config_data:
                    self.script_edit.setText(config_data['script'])
                else:
                    self.script_edit.clear()
            except Exception as e:
                print("解析配置JSON時發生錯誤")
                self.script_edit.clear()
        else:
            self.script_edit.clear()
    
    def copy_config(self, config_id):
        """複製配置"""
        # 從資料庫載入配置詳情
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, file_type, description, configuration, status
            FROM process_configs
            WHERE id = ?
        """, (config_id,))
        
        config = cursor.fetchone()
        
        if not config:
            conn.close()
            return
        
        # 設置為新配置（ID為空）
        self.current_config_id = None
        
        # 複製配置資訊，但修改名稱
        self.name_edit.setText(f"{config[1]} - 複製")
        
        # 設置適用文件類型
        file_type_index = 0  # 默認"所有類型"
        if config[2] == "Excel":
            file_type_index = 1
        elif config[2] == "CSV":
            file_type_index = 2
        elif config[2] == "PDF":
            file_type_index = 3
        self.type_combo.setCurrentIndex(file_type_index)
        
        # 設置狀態為測試中
        self.status_combo.setCurrentIndex(1)  # "測試中"
        
        # 設置描述
        self.desc_edit.setText(config[3] or "")
        
        # 清空步驟列表
        self.steps_list.clear()
        
        # 解析配置JSON並填充步驟列表
        if config[4]:
            try:
                config_data = json.loads(config[4])
                
                # 填充處理步驟
                if 'steps' in config_data:
                    for step in config_data['steps']:
                        step_item = QListWidgetItem(f"{step['order']}. {step['name']}")
                        step_item.setData(Qt.UserRole, step)
                        self.steps_list.addItem(step_item)
                
                # 填充腳本
                if 'script' in config_data:
                    self.script_edit.setText(config_data['script'])
                else:
                    self.script_edit.clear()
            except Exception as e:
                print("解析配置JSON時發生錯誤")
                self.script_edit.clear()
        else:
            self.script_edit.clear()
        
        conn.close()
    
    def save_config(self):
        """保存配置"""
        # 獲取輸入值
        name = self.name_edit.text()
        file_type = self.type_combo.currentText()
        status = ["enabled", "testing", "disabled"][self.status_combo.currentIndex()]
        description = self.desc_edit.toPlainText()
        
        # 驗證必填字段
        if not name:
            QMessageBox.warning(self, "保存失敗", "配置名稱不能為空")
            return
        
        # 收集步驟資訊
        steps = []
        for i in range(self.steps_list.count()):
            step_item = self.steps_list.item(i)
            step_data = step_item.data(Qt.UserRole)
            steps.append(step_data)
        
        # 獲取腳本
        script = self.script_edit.toPlainText()
        
        # 構建配置JSON
        config_data = {
            'steps': steps,
            'script': script
        }
        
        # 轉換為JSON字符串
        configuration = json.dumps(config_data)
        
        # 保存到資料庫
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.current_config_id:  # 更新現有配置
                cursor.execute("""
                    UPDATE process_configs
                    SET name = ?, file_type = ?, description = ?, configuration = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (name, file_type, description, configuration, status, self.current_config_id))
            else:  # 創建新配置
                cursor.execute("""
                    INSERT INTO process_configs (name, file_type, description, configuration, status, is_default)
                    VALUES (?, ?, ?, ?, ?, 0)
                """, (name, file_type, description, configuration, status))
            
            conn.commit()
            
            # 更新配置列表
            self.load_configs()
            
            # 清空表單
            self.clear_form()
            
            QMessageBox.information(self, "保存成功", "配置已成功保存")
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "保存失敗", f"保存配置時發生錯誤：{str(e)}")
        
        finally:
            conn.close()