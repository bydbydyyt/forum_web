from django.db import models
from django.conf import settings
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    """
    论坛分区模型
    用于对帖子进行分类
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='分区名称')
    description = models.TextField(blank=True, verbose_name='分区描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '分区'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name

class Post(models.Model):
    """
    帖子模型
    用于存储论坛帖子内容
    """
    title = models.CharField(max_length=200, verbose_name='标题')
    content = RichTextField(verbose_name='内容')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name='所属分区')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 统计信息
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    comment_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    
    # 状态
    is_pinned = models.BooleanField(default=False, verbose_name='是否置顶')
    is_hidden = models.BooleanField(default=False, verbose_name='是否隐藏')
    
    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = verbose_name
        ordering = ['-is_pinned', '-created_at']
        
    def __str__(self):
        return self.title
        
    def increase_view_count(self):
        """增加浏览量"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
        
    def update_comment_count(self):
        """更新评论数"""
        self.comment_count = self.comments.count()
        self.save(update_fields=['comment_count'])

class Comment(models.Model):
    """
    评论模型
    用于存储帖子评论
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='所属帖子')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 父评论，用于实现评论嵌套
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='父评论')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
        
    def __str__(self):
        return f'{self.author.username} 评论了 {self.post.title}'

class Like(models.Model):
    """
    点赞模型
    用于记录用户对帖子的点赞
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liked_posts', verbose_name='用户')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='帖子')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'post']
        
    def __str__(self):
        return f'{self.user.username} 点赞了 {self.post.title}'

class Collection(models.Model):
    """
    收藏夹模型
    用于用户收藏帖子
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections', verbose_name='用户')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='collections', verbose_name='帖子')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'post']
        
    def __str__(self):
        return f'{self.user.username} 收藏了 {self.post.title}'

class PostImage(models.Model):
    """
    帖子图片模型
    用于存储帖子中的图片
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name='所属帖子')
    image = models.ImageField(upload_to='post_images/', verbose_name='图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '帖子图片'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f'{self.post.title} 的图片'

class PostVideo(models.Model):
    """
    帖子视频模型
    用于存储帖子中的视频
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='videos', verbose_name='所属帖子')
    video = models.FileField(upload_to='post_videos/', verbose_name='视频')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '帖子视频'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f'{self.post.title} 的视频'

class Topic(models.Model):
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    views = models.PositiveIntegerField('浏览量', default=0)

    class Meta:
        verbose_name = '主题'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Reply(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='replies', verbose_name='主题')
    content = models.TextField('内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '回复'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} 回复了 {self.topic.title}'
