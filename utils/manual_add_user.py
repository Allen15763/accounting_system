from utils.db import DatabaseManager

# 創建資料庫管理實例
db = DatabaseManager()

# 添加新用戶
username = "test_user"
password = db.hash_password("password")  # 密碼會被雜湊處理
name = "Test User"
email = "test@example.com"
role = "檢視者"
status = "啟用"

conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO users (username, password, name, email, role, status)
    VALUES (?, ?, ?, ?, ?, ?)
""", (username, password, name, email, role, status))

conn.commit()
conn.close()

print(f"已成功添加用戶: {username}")