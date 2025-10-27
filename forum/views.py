from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from .models import Topic, Reply, Category, Tag
from .forms import TopicForm, ReplyForm

def is_staff_or_superuser(user):
    """检查用户是否为管理员或超级用户"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def can_create_topic(user):
    """检查用户是否可以创建帖子"""
    if not user.is_authenticated:
        return False
    
    # 管理员和超级用户不受限制
    if user.is_staff or user.is_superuser:
        return True
    
    # 检查用户注册天数（例如：注册满1天才能发帖）
    from django.utils import timezone
    days_since_joined = (timezone.now() - user.date_joined).days
    return days_since_joined >= 1

def can_create_reply(user):
    """检查用户是否可以回复"""
    if not user.is_authenticated:
        return False
    
    # 管理员和超级用户不受限制
    if user.is_staff or user.is_superuser:
        return True
    
    # 检查用户注册天数（例如：注册满1天才能回复）
    from django.utils import timezone
    days_since_joined = (timezone.now() - user.date_joined).days
    return days_since_joined >= 1

def forum_list(request):
    # 获取筛选参数
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    tag_id = request.GET.get('tag', '')
    
    # 获取所有主题，按置顶状态和创建时间排序（置顶帖子在前）
    topics = Topic.objects.all().order_by('-is_pinned', '-created_at')
    
    # 如果有搜索查询，过滤主题
    if search_query:
        topics = topics.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # 按分类筛选
    if category_id:
        topics = topics.filter(category_id=category_id)
    
    # 按标签筛选
    if tag_id:
        topics = topics.filter(tags__id=tag_id)
    
    # 获取所有分类和标签用于筛选
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    # 分页设置
    paginator = Paginator(topics, 10)  # 每页显示10个主题
    page = request.GET.get('page')
    
    try:
        topics_page = paginator.page(page)
    except PageNotAnInteger:
        topics_page = paginator.page(1)
    except EmptyPage:
        topics_page = paginator.page(paginator.num_pages)
    
    return render(request, 'forum/forum_list.html', {
        'topics': topics_page,
        'search_query': search_query,
        'categories': categories,
        'tags': tags,
        'selected_category': category_id,
        'selected_tag': tag_id
    })

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    # 增加浏览量
    topic.increase_views()
    
    # 处理点赞操作
    if request.method == 'POST' and 'like' in request.POST:
        if request.user.is_authenticated:
            topic.toggle_like(request.user)
            return redirect('forum:topic_detail', topic_id=topic.id)
    
    # 获取回复并分页
    replies_list = topic.replies.all().order_by('created_at')
    paginator = Paginator(replies_list, 10)  # 每页显示10条回复
    page = request.GET.get('page')
    
    try:
        replies = paginator.page(page)
    except PageNotAnInteger:
        replies = paginator.page(1)
    except EmptyPage:
        replies = paginator.page(paginator.num_pages)
    
    # 检查当前用户是否已点赞
    user_has_liked = topic.user_has_liked(request.user)
    
    return render(request, 'forum/topic_detail.html', {
        'topic': topic,
        'replies': replies,
        'user_has_liked': user_has_liked
    })

@login_required
def topic_create(request):
    # 检查用户是否有权限创建帖子
    if not can_create_topic(request.user):
        messages.error(request, '您暂时没有权限创建帖子。新用户需要注册满1天才能发帖。')
        return redirect('forum:forum_list')
    
    # 获取所有分类和标签用于表单
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            # 保存多对多关系（标签）
            form.save_m2m()
            messages.success(request, '主题创建成功！')
            return redirect('forum:topic_detail', topic_id=topic.id)
    else:
        form = TopicForm()
    return render(request, 'forum/topic_form.html', {
        'form': form,
        'categories': categories,
        'tags': tags
    })

@login_required
def reply_create(request, topic_id):
    # 检查用户是否有权限回复
    if not can_create_reply(request.user):
        messages.error(request, '您暂时没有权限回复帖子。新用户需要注册满1天才能回复。')
        return redirect('forum:topic_detail', topic_id=topic_id)
    
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.topic = topic
            reply.save()
            messages.success(request, '回复发布成功！')
            return redirect('forum:topic_detail', topic_id=topic.id)
    else:
        form = ReplyForm()
    return render(request, 'forum/reply_form.html', {
        'form': form,
        'topic': topic
    })

@login_required
@user_passes_test(is_staff_or_superuser)
def toggle_topic_pin(request, topic_id):
    """切换帖子置顶状态"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        topic.is_pinned = not topic.is_pinned
        topic.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_pinned': topic.is_pinned,
                'message': f'帖子已{"置顶" if topic.is_pinned else "取消置顶"}'
            })
        
        messages.success(request, f'帖子已{"置顶" if topic.is_pinned else "取消置顶"}')
        return redirect('forum:topic_detail', topic_id=topic.id)
    
    return redirect('forum:topic_detail', topic_id=topic.id)

@login_required
@user_passes_test(is_staff_or_superuser)
def toggle_topic_essence(request, topic_id):
    """切换帖子精华状态"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        topic.is_essence = not topic.is_essence
        topic.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_essence': topic.is_essence,
                'message': f'帖子已{"设为精华" if topic.is_essence else "取消精华"}'
            })
        
        messages.success(request, f'帖子已{"设为精华" if topic.is_essence else "取消精华"}')
        return redirect('forum:topic_detail', topic_id=topic.id)
    
    return redirect('forum:topic_detail', topic_id=topic.id)

@login_required
def delete_topic(request, topic_id):
    """删除帖子"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    # 检查权限：只有管理员或帖子作者可以删除
    if not (request.user.is_staff or request.user.is_superuser or topic.author == request.user):
        messages.error(request, '您没有权限删除此帖子')
        return redirect('forum:topic_detail', topic_id=topic.id)
    
    if request.method == 'POST':
        topic.delete()
        messages.success(request, '帖子删除成功')
        return redirect('forum:forum_list')
    
    return redirect('forum:topic_detail', topic_id=topic.id)

@login_required
def delete_reply(request, reply_id):
    """删除回复"""
    reply = get_object_or_404(Reply, id=reply_id)
    topic_id = reply.topic.id
    
    # 检查权限：只有管理员或回复作者可以删除
    if not (request.user.is_staff or request.user.is_superuser or reply.author == request.user):
        messages.error(request, '您没有权限删除此回复')
        return redirect('forum:topic_detail', topic_id=topic_id)
    
    if request.method == 'POST':
        reply.delete()
        messages.success(request, '回复删除成功')
    
    return redirect('forum:topic_detail', topic_id=topic_id)
