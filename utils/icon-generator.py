import os
from PIL import Image, ImageDraw, ImageFont
import io

# 確保輸出目錄存在
OUTPUT_DIR = "assets/icons"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 定義圖標尺寸
SIZES = [16, 32, 48, 64, 128, 256]

# 顏色定義
COLORS = {
    "primary": (52, 152, 219),  # 藍色
    "secondary": (44, 62, 80),  # 深藍色
    "success": (39, 174, 96),   # 綠色
    "danger": (231, 76, 60),    # 紅色
    "warning": (243, 156, 18),  # 黃色
    "light": (236, 240, 241),   # 淺灰色
    "dark": (52, 73, 94),       # 深灰色
    "white": (255, 255, 255),   # 白色
    "black": (0, 0, 0)          # 黑色
}

def create_icon(name, color, symbol=None, background_color=None, font_color=COLORS["white"]):
    """創建圖標並保存為.ico文件"""
    images = []
    
    for size in SIZES:
        # 創建圖像
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 繪製背景 (如果提供)
        if background_color:
            draw.ellipse([(0, 0), (size, size)], fill=background_color)
        
        # 繪製主要形狀
        padding = size // 4
        if name == "app_icon":
            # 特殊處理應用程式圖標
            draw.rectangle([(padding, padding), (size-padding, size-padding)], fill=color)
            inner_padding = size // 8
            draw.rectangle([(padding+inner_padding, padding+inner_padding), 
                           (size-padding-inner_padding, size-padding-inner_padding)], 
                           fill=COLORS["white"])
        elif name in ["folder", "file"]:
            if name == "folder":
                # 繪製文件夾圖標
                draw.rectangle([(padding, padding + padding//2), 
                               (size-padding, size-padding)], fill=color)
                draw.rectangle([(padding + padding//2, padding), 
                               (size-padding, padding + padding//2)], fill=color)
            else:
                # 繪製文件圖標
                draw.rectangle([(padding, padding), (size-padding, size-padding)], fill=color)
                line_padding = size // 10
                for i in range(3):
                    line_y = padding + line_padding + i * (line_padding * 2)
                    draw.line([(padding + line_padding, line_y), 
                              (size-padding-line_padding, line_y)], 
                              fill=COLORS["light"], width=max(1, size//32))
        elif name in ["success", "warning", "error"]:
            # 狀態圖標
            draw.ellipse([(padding, padding), (size-padding, size-padding)], fill=color)
            
            if name == "success":
                # 繪製對勾
                points = [
                    (padding + size//6, size//2),
                    (size//2, size - padding - size//6),
                    (size - padding - size//6, padding + size//3)
                ]
                draw.line(points, fill=font_color, width=max(1, size//16))
            elif name == "error":
                # 繪製X
                draw.line([(padding + size//6, padding + size//6), 
                          (size - padding - size//6, size - padding - size//6)], 
                          fill=font_color, width=max(1, size//16))
                draw.line([(padding + size//6, size - padding - size//6), 
                          (size - padding - size//6, padding + size//6)], 
                          fill=font_color, width=max(1, size//16))
            elif name == "warning":
                # 繪製!
                dot_size = max(1, size//16)
                draw.ellipse([(size//2 - dot_size, size - padding - dot_size*2), 
                             (size//2 + dot_size, size - padding)], fill=font_color)
                draw.rectangle([(size//2 - dot_size, padding + size//5), 
                               (size//2 + dot_size, size - padding - dot_size*3)], fill=font_color)
        elif symbol:
            # 如果提供了符號，繪製帶符號的圖標
            draw.ellipse([(padding, padding), (size-padding, size-padding)], fill=color)
            
            # 使用簡單形狀繪製符號
            inner_padding = size // 3
            if symbol in "+-":
                # + 或 - 符號
                # 確保水平線的繪製
                h_x1 = padding + inner_padding
                h_x2 = size - padding - inner_padding
                
                # 確保 x1 < x2
                if h_x1 >= h_x2:
                    h_x1, h_x2 = h_x2, h_x1
                    
                draw.rectangle([(h_x1, size//2 - size//12), 
                            (h_x2, size//2 + size//12)], 
                            fill=font_color)
                            
                # 對於 + 符號，添加垂直線
                if symbol == "+":
                    v_y1 = padding + inner_padding
                    v_y2 = size - padding - inner_padding
                    
                    # 確保 y1 < y2
                    if v_y1 >= v_y2:
                        v_y1, v_y2 = v_y2, v_y1
                    
                    v_x1 = size//2 - size//12
                    v_x2 = size//2 + size//12
                    
                    # 確保 x1 < x2
                    if v_x1 >= v_x2:
                        v_x1, v_x2 = v_x2, v_x1
                        
                    draw.rectangle([(v_x1, v_y1), (v_x2, v_y2)], fill=font_color)
            elif symbol == "↓":
                # 下箭頭 (用於下載)
                points = [
                    (size//2, size - padding - inner_padding//2),
                    (padding + inner_padding, size//2),
                    (size//2 - size//8, size//2),
                    (size//2 - size//8, padding + inner_padding),
                    (size//2 + size//8, padding + inner_padding),
                    (size//2 + size//8, size//2),
                    (size - padding - inner_padding, size//2)
                ]
                draw.polygon(points, fill=font_color)
            elif symbol == "↑":
                # 上箭頭 (用於上傳)
                points = [
                    (size//2, padding + inner_padding//2),
                    (padding + inner_padding, size//2),
                    (size//2 - size//8, size//2),
                    (size//2 - size//8, size - padding - inner_padding),
                    (size//2 + size//8, size - padding - inner_padding),
                    (size//2 + size//8, size//2),
                    (size - padding - inner_padding, size//2)
                ]
                draw.polygon(points, fill=font_color)
            else:
                # 對於其他符號，繪製圓形並在上面繪製一個字母
                # 使用簡單形狀代替文字
                if symbol == "E":  # 編輯
                    line_spacing = max(2, size//20)
                    for i in range(3):
                        y_pos = padding + inner_padding + i * line_spacing * 3
                        draw.line([(padding + inner_padding, y_pos), 
                                  (size - padding - inner_padding, y_pos)], 
                                  fill=font_color, width=max(1, size//32))
                elif symbol == "S":  # 分享
                    # 繪製分享圖標的簡化版本
                    center_x, center_y = size//2, size//2
                    radius = size//6
                    
                    # 繪製三個點
                    draw.ellipse([(center_x - radius, padding + inner_padding - radius), 
                                 (center_x + radius, padding + inner_padding + radius)], 
                                 fill=font_color)
                    
                    draw.ellipse([(padding + inner_padding - radius, size - padding - inner_padding - radius), 
                                 (padding + inner_padding + radius, size - padding - inner_padding + radius)], 
                                 fill=font_color)
                    
                    draw.ellipse([(size - padding - inner_padding - radius, size - padding - inner_padding - radius), 
                                 (size - padding - inner_padding + radius, size - padding - inner_padding + radius)], 
                                 fill=font_color)
                    
                    # 連接這些點
                    draw.line([(center_x, padding + inner_padding), 
                              (padding + inner_padding, size - padding - inner_padding)], 
                              fill=font_color, width=max(1, size//32))
                    
                    draw.line([(center_x, padding + inner_padding), 
                              (size - padding - inner_padding, size - padding - inner_padding)], 
                              fill=font_color, width=max(1, size//32))
                elif symbol == "D":  # 儀表板
                    # 繪製簡化的儀表板圖標
                    grid_size = (size - 2*padding) // 2
                    margin = size//20
                    
                    draw.rectangle([(padding, padding), 
                                  (padding + grid_size - margin, padding + grid_size - margin)], 
                                  fill=font_color)
                    
                    draw.rectangle([(padding + grid_size + margin, padding), 
                                  (size - padding, padding + grid_size - margin)], 
                                  fill=font_color)
                    
                    draw.rectangle([(padding, padding + grid_size + margin), 
                                  (padding + grid_size - margin, size - padding)], 
                                  fill=font_color)
                    
                    draw.rectangle([(padding + grid_size + margin, padding + grid_size + margin), 
                                  (size - padding, size - padding)], 
                                  fill=font_color)
                elif symbol == "⚙":  # 設置
                    # 繪製簡化的齒輪圖標
                    outer_radius = (size - 2*padding) // 2
                    inner_radius = outer_radius // 2
                    center_x, center_y = size//2, size//2
                    
                    # 繪製外圓
                    draw.ellipse([(center_x - outer_radius, center_y - outer_radius), 
                                 (center_x + outer_radius, center_y + outer_radius)], 
                                 outline=font_color, width=max(1, size//16))
                    
                    # 繪製內圓
                    draw.ellipse([(center_x - inner_radius, center_y - inner_radius), 
                                 (center_x + inner_radius, center_y + inner_radius)], 
                                 fill=font_color)
                elif symbol == "👤" or symbol == "👤+":  # 用戶相關
                    # 繪製用戶圖標
                    # 頭部
                    head_radius = size//6
                    draw.ellipse([(size//2 - head_radius, padding + inner_padding), 
                                 (size//2 + head_radius, padding + inner_padding + head_radius*2)], 
                                 fill=font_color)
                    
                    # 身體 (梯形)
                    body_top = padding + inner_padding + head_radius*2
                    body_width_top = head_radius * 1.5
                    body_width_bottom = head_radius * 2.5
                    
                    body_points = [
                        (size//2 - body_width_top, body_top),
                        (size//2 + body_width_top, body_top),
                        (size//2 + body_width_bottom, size - padding - inner_padding),
                        (size//2 - body_width_bottom, size - padding - inner_padding)
                    ]
                    draw.polygon(body_points, fill=font_color)
                    
                    # 如果是新增用戶圖標，添加一個加號
                    if symbol == "👤+":
                        plus_size = size//10
                        draw.ellipse([(size - padding - plus_size*2, padding + plus_size), 
                                     (size - padding, padding + plus_size*3)], 
                                     fill=COLORS["success"])
                        
                        # 在加號圓圈上繪製十字
                        plus_center_x = size - padding - plus_size
                        plus_center_y = padding + plus_size*2
                        
                        draw.line([(plus_center_x - plus_size//2, plus_center_y), 
                                  (plus_center_x + plus_size//2, plus_center_y)], 
                                  fill=COLORS["white"], width=max(1, size//64))
                        
                        draw.line([(plus_center_x, plus_center_y - plus_size//2), 
                                  (plus_center_x, plus_center_y + plus_size//2)], 
                                  fill=COLORS["white"], width=max(1, size//64))
        else:
            # 默認圖標
            draw.ellipse([(padding, padding), (size-padding, size-padding)], fill=color)
        
        # 添加到圖像列表
        images.append(img)
    
    # 保存為.ico文件
    ico_path = os.path.join(OUTPUT_DIR, f"{name}.ico")
    images[0].save(ico_path, format="ICO", sizes=[(s, s) for s in SIZES], append_images=images[1:])
    
    print(f"創建圖標: {ico_path}")
    return ico_path

# 創建應用程序圖標
create_icon("app_icon", COLORS["primary"])

# 創建檔案和文件夾圖標
create_icon("folder", COLORS["primary"])
create_icon("file", COLORS["secondary"])
create_icon("excel", COLORS["success"])
create_icon("pdf", COLORS["danger"])

# 創建操作圖標
create_icon("upload", COLORS["primary"], "↑")
create_icon("download", COLORS["primary"], "↓")
create_icon("add", COLORS["success"], "+")
create_icon("edit", COLORS["primary"], "E")
create_icon("delete", COLORS["danger"], "-")
create_icon("share", COLORS["primary"], "S")

# 創建狀態圖標
create_icon("success", COLORS["success"])
create_icon("warning", COLORS["warning"])
create_icon("error", COLORS["danger"])

# 創建導航圖標
create_icon("dashboard", COLORS["primary"], "D")
create_icon("settings", COLORS["secondary"], "⚙")

# 創建用戶相關圖標
create_icon("user", COLORS["primary"], "👤")
create_icon("user_add", COLORS["success"], "👤+")

print("所有圖標已成功生成！")