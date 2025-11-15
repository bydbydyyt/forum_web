#!/usr/bin/env python
"""
创建示例分类和标签数据的脚本
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum_web.settings')
django.setup()

from forum.models import Category, Tag

def create_sample_data():
    """创建示例分类和标签数据"""
    
    # 创建分类
    categories = [
        {'name': '技术讨论', 'description': '技术相关话题讨论'},
        {'name': '学习交流', 'description': '学习经验和方法分享'},
        {'name': '生活分享', 'description': '日常生活和兴趣爱好'},
        {'name': '问题求助', 'description': '遇到问题寻求帮助'},
        {'name': '意见建议', 'description': '对论坛的建议和意见'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"创建分类: {category.name}")
    
    # 创建标签
    tags = [
        {'name': 'Python', 'color': '#3776AB'},
        {'name': 'Django', 'color': '#092E20'},
        {'name': 'JavaScript', 'color': '#F7DF1E'},
        {'name': 'HTML/CSS', 'color': '#E34F26'},
        {'name': '数据库', 'color': '#336791'},
        {'name': '算法', 'color': '#FF6B6B'},
        {'name': '前端', 'color': '#61DAFB'},
        {'name': '后端', 'color': '#4479A1'},
        {'name': '学习笔记', 'color': '#4CAF50'},
        {'name': '经验分享', 'color': '#FF9800'},
        {'name': '问题解决', 'color': '#F44336'},
        {'name': '新手求助', 'color': '#9C27B0'},
    ]
    
    for tag_data in tags:
        tag, created = Tag.objects.get_or_create(
            name=tag_data['name'],
            defaults={'color': tag_data['color']}
        )
        if created:
            print(f"创建标签: {tag.name} (颜色: {tag.color})")
    
    print("\n示例数据创建完成！")

if __name__ == '__main__':
    create_sample_data()