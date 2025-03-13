# build.py
import PyInstaller.__main__
import os
import shutil

# 清理先前的構建文件
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# PyInstaller配置
PyInstaller.__main__.run([
    'main.py',
    '--name=會計底稿處理系統',
    '--onefile',
    '--windowed',
    '--icon=assets/icons/app_icon.ico',
    '--add-data=assets/icons;assets/icons',
    '--add-data=assets/styles;assets/styles',
    '--add-data=assets/images;assets/images',
    '--add-data=data/schema.sql;data',
    '--hidden-import=PySide6.QtSvg',
    '--hidden-import=sqlite3',
])

# 創建額外目錄
os.makedirs("dist/data/uploads", exist_ok=True)