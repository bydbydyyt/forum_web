from PIL import Image, ImageDraw, ImageFont
import os

def create_default_background():
    """创建默认背景图片"""
    # 创建一个800x400的图片
    img = Image.new('RGB', (800, 400), color='#f0f2f5')
    draw = ImageDraw.Draw(img)
    
    # 添加一些简单的几何图形
    draw.rectangle([(0, 0), (800, 200)], fill='#e6e9ef')
    draw.rectangle([(0, 200), (800, 400)], fill='#d8dce6')
    
    # 保存图片
    img.save('static/img/default-background.jpg', 'JPEG', quality=95)

def create_default_avatar():
    """创建默认头像图片"""
    # 创建一个200x200的图片
    img = Image.new('RGB', (200, 200), color='#e6e9ef')
    draw = ImageDraw.Draw(img)
    
    # 绘制一个简单的头像轮廓
    draw.ellipse([(20, 20), (180, 180)], fill='#d8dce6')
    
    # 绘制眼睛
    draw.ellipse([(70, 70), (90, 90)], fill='#4a4a4a')
    draw.ellipse([(110, 70), (130, 90)], fill='#4a4a4a')
    
    # 绘制微笑
    draw.arc([(60, 100), (140, 140)], 0, 180, fill='#4a4a4a', width=5)
    
    # 保存图片
    img.save('static/img/default-avatar.png', 'PNG')

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs('static/img', exist_ok=True)
    
    # 创建默认图片
    create_default_background()
    create_default_avatar()
    
    print("默认图片已生成！") 