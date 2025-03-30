import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog
from utils.db import DatabaseManager

def setup_environment():
    """設置應用程式環境"""
    # 確保所需目錄存在
    os.makedirs('data', exist_ok=True)
    
    # 初始化資料庫
    db_manager = DatabaseManager()
    db_manager.initialize_database()

def main():
    """主應用程式入口"""
    # 設置環境
    setup_environment()
    
    # 創建應用程式
    app = QApplication(sys.argv)
    app.setApplicationName("會計底稿處理系統")
    app.setWindowIcon(QIcon("assets/icons/app_icon.ico"))
    
    # 加載暗色系樣式表
    try:
        with open("assets/styles/main.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"無法加載樣式表: {e}")
    
    # 顯示登入視窗
    login_dialog = LoginDialog()
    if login_dialog.exec_():
        # 登入成功，顯示主視窗
        window = MainWindow(login_dialog.get_user())
        window.show()
        return app.exec_()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())