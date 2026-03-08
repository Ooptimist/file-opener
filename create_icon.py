from PIL import Image, ImageDraw, ImageFont
import os

# 创建一个256x256的图标
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 绘制文件夹背景（蓝色渐变效果）
folder_color = (52, 152, 219)  # 蓝色
folder_dark = (41, 128, 185)   # 深蓝色

# 文件夹主体（圆角矩形）
draw.rounded_rectangle([20, 60, 236, 220], radius=20, fill=folder_color)

# 文件夹顶部标签
draw.rounded_rectangle([40, 40, 140, 80], radius=15, fill=folder_dark)

# 保存为多尺寸ico
img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])

print("图标已创建: icon.ico")
