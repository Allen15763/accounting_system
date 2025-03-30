import sqlite3
import os
import hashlib
from pathlib import Path

class DatabaseManager:
    """資料庫管理類"""
    
    def __init__(self, db_file='data/accounting_system.db'):
        self.db_file = db_file
        
    def get_connection(self):
        """獲取資料庫連接"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # 使查詢結果可以通過列名訪問
        return conn
    
    def initialize_database(self):
        """初始化資料庫架構"""
        # 如果資料庫已存在則返回
        if os.path.exists(self.db_file):
            return
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        # 讀取並執行架構建立腳本
        schema_path = Path('data/schema.sql')
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_script = f.read()
            
            conn = self.get_connection()
            conn.executescript(schema_script)
            
            # 創建默認管理員帳號
            self.create_admin_user()
            
            conn.close()
        else:
            # 如果架構腳本不存在，手動創建表格
            self.create_tables()
    
    def create_tables(self):
        """手動創建資料表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 創建用戶表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 創建文件表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            path TEXT NOT NULL,
            user_id INTEGER,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 創建處理配置表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS process_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            file_type TEXT,
            configuration TEXT,
            user_id INTEGER,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 創建數據連接表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            server TEXT NOT NULL,
            port TEXT,
            database_name TEXT,
            username TEXT,
            password TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 創建任務表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_id INTEGER,
            config_id INTEGER,
            priority TEXT,
            status TEXT NOT NULL,
            progress REAL DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files(id),
            FOREIGN KEY (config_id) REFERENCES process_configs(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

        # 添加 task_steps 表格的創建語句
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            order_num INTEGER,
            name TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            duration TEXT,
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        )
        ''')
        
        # 創建結果表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            output_path TEXT NOT NULL,
            status TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 創建系統日誌表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
        
        # 創建默認管理員帳號
        self.create_admin_user()
        
        conn.close()
    
    def create_admin_user(self):
        """創建默認管理員帳號"""
        # 簡單加密密碼，實際應用中應使用更安全的方法
        password = self.hash_password("admin")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO users (username, password, name, email, role, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', password, 'Allen Li (李季倫)', 'admin@example.com', '系統管理員', '啟用'))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """簡單的密碼加密"""
        # 實際應用中應使用更安全的加密方法並添加鹽值
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        """驗證用戶登入"""
        hashed_password = self.hash_password(password)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, username, name, email, role, status
        FROM users
        WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and user['status'] == '啟用':
            return dict(user)
        return None