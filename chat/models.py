from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Friendship(models.Model):
    """
    好友关系模型
    用于管理用户之间的好友关系
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends', verbose_name='用户')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of', verbose_name='好友')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_accepted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = '好友关系'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'friend']
        
    def __str__(self):
        return f'{self.user.username} 和 {self.friend.username} 是好友'

class FriendRequest(models.Model):
    """
    好友请求模型
    用于管理用户之间的好友申请
    """
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
    )
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests', verbose_name='接收者')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '好友请求'
        verbose_name_plural = verbose_name
        unique_together = ['sender', 'receiver']
        
    def __str__(self):
        return f'{self.sender.username} 向 {self.receiver.username} 发送好友请求'

class ChatRoom(models.Model):
    """
    聊天室模型
    用于管理用户之间的私聊会话
    """
    name = models.CharField(max_length=255, unique=True, default='default_room')
    participants = models.ManyToManyField(User, related_name='chat_rooms', verbose_name='参与者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '聊天室'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f'聊天室 {self.name}'

class Message(models.Model):
    """
    消息模型
    用于存储聊天消息
    """
    MESSAGE_TYPES = (
        ('text', '文本'),
        ('image', '图片'),
        ('video', '视频'),
        ('file', '文件'),
    )
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name='聊天室')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    file = models.FileField(upload_to='chat_files/', null=True, blank=True, verbose_name='文件')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    file_url = models.URLField(null=True, blank=True)
    
    class Meta:
        verbose_name = '消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
        
    def __str__(self):
        return f'{self.sender.username} 在 {self.room} 发送了消息'

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=[
        ('friend_request', '好友请求'),
        ('message', '新消息'),
        ('system', '系统通知')
    ])
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
