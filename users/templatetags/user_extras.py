from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter
def days_since_joined(user):
    """
    计算用户注册至今的天数
    """
    if not user or not user.date_joined:
        return 0
    
    # 获取当前时间
    now = timezone.now()
    
    # 计算时间差
    delta = now - user.date_joined
    
    # 返回天数
    return delta.days

@register.filter
def user_post_count(user):
    """
    获取用户发帖数量
    """
    if not user:
        return 0
    return user.posts.count() if hasattr(user, 'posts') else 0

@register.filter
def user_comment_count(user):
    """
    获取用户评论数量
    """
    if not user:
        return 0
    return user.comments.count() if hasattr(user, 'comments') else 0

@register.filter
def extract_size(filename):
    """
    从文件名中提取尺寸信息
    例如: background_1200x400.jpg -> 1200x400
    """
    if not filename:
        return ''
    
    import re
    # 匹配文件名中的尺寸格式 (数字x数字)
    size_pattern = r'(\d+x\d+)'
    match = re.search(size_pattern, str(filename))
    
    if match:
        return match.group(1)
    
    # 如果没有找到尺寸信息，返回默认值
    return '1200x400'