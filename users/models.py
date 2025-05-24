from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """
    自定义用户模型
    扩展Django默认用户模型，添加额外字段
    """
    # 基本信息
    nickname = models.CharField(_('昵称'), max_length=50, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='users/avatars/', null=True, blank=True)
    background = models.ImageField(_('背景图片'), upload_to='users/backgrounds/', null=True, blank=True, default='backgrounds/default-background.jpg')
    bio = models.TextField(_('个人简介'), max_length=500, blank=True)
    friend_code = models.CharField(_('好友代码'), max_length=8, unique=True, default=lambda: str(uuid.uuid4())[:8])
    
    # 用户名修改相关
    last_username_change = models.DateTimeField(null=True, blank=True, verbose_name='上次修改用户名时间')
    username_changes_count = models.PositiveIntegerField(default=0, verbose_name='用户名修改次数')
    
    # 统计信息
    show_collections = models.BooleanField(_('公开收藏'), default=True)
    show_friends = models.BooleanField(_('公开好友'), default=True)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        
    def __str__(self):
        return self.username
        
    @property
    def post_count(self):
        """获取用户发帖数"""
        return self.posts.count()
        
    @property
    def comment_count(self):
        """获取用户评论数"""
        return self.comments.count()
        
    @property
    def like_count(self):
        """获取用户获赞数"""
        return self.likes.count()
        
    @property
    def days_since_joined(self):
        """获取用户注册天数"""
        return (timezone.now() - self.date_joined).days
        
    def can_change_username(self):
        """检查是否可以修改用户名"""
        if not self.last_username_change:
            return True
        days_since_last_change = (timezone.now() - self.last_username_change).days
        return days_since_last_change >= 7
        
    def change_username(self, new_username):
        """修改用户名"""
        if not self.can_change_username():
            return False, "每周只能修改一次用户名"
            
        if User.objects.filter(username=new_username).exists():
            return False, "该用户名已被使用"
            
        self.username = new_username
        self.last_username_change = timezone.now()
        self.username_changes_count += 1
        self.save()
        return True, "用户名修改成功"
