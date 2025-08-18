from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
import os
from .models import ChatRoom, Message, Friendship, UserStatus, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_room(request, username):
    chat_user = get_object_or_404(User, username=username)
    room_name = f"{min(request.user.username, username)}_{max(request.user.username, username)}"
    room, created = ChatRoom.objects.get_or_create(name=room_name)
    
    # 获取聊天记录
    messages = Message.objects.filter(room=room).order_by('created_at')
    
    # 获取好友列表
    friendships = Friendship.objects.filter(user=request.user)
    
    context = {
        'chat_user': chat_user,
        'messages': messages,
        'friendships': friendships,
    }
    return render(request, 'chat/chat.html', context)

@login_required
@require_POST
def upload_file(request, username):
    files = request.FILES.getlist('files')
    uploaded_files = []
    
    for file in files:
        # 生成文件路径
        file_path = f'chat_files/{request.user.username}/{file.name}'
        
        # 保存文件
        path = default_storage.save(file_path, ContentFile(file.read()))
        
        # 确定文件类型
        file_type = 'file'
        if file.content_type.startswith('image/'):
            file_type = 'image'
        elif file.content_type.startswith('video/'):
            file_type = 'video'
        
        uploaded_files.append({
            'type': file_type,
            'url': default_storage.url(path)
        })
    
    return JsonResponse({
        'status': 'success',
        'files': uploaded_files
    })

@login_required
def chat_home(request):
    """私聊首页视图"""
    # 获取好友列表
    friendships = Friendship.objects.filter(user=request.user)
    friends = [friendship.friend for friendship in friendships]
    
    context = {
        'friends': friends,
    }
    return render(request, 'chat/chat_home.html', context)

@login_required
def send_friend_request(request, username):
    friend = get_object_or_404(User, username=username)
    
    # 检查是否已经是好友
    if Friendship.objects.filter(user=request.user, friend=friend).exists():
        messages.error(request, '你们已经是好友了')
        return redirect('chat:home')
    
    # 检查是否已经发送过请求
    if Friendship.objects.filter(user=request.user, friend=friend, is_accepted=False).exists():
        messages.error(request, '已经发送过好友请求了')
        return redirect('chat:home')
    
    # 创建好友请求
    Friendship.objects.create(user=request.user, friend=friend, is_accepted=False)
    
    # 创建通知
    Notification.objects.create(
        user=friend,
        message=f'{request.user.username} 请求添加你为好友',
        notification_type='friend_request',
        related_user=request.user
    )
    
    messages.success(request, '好友请求已发送')
    return redirect('chat:home')

@login_required
def accept_friend_request(request, username):
    friend = get_object_or_404(User, username=username)
    friendship = get_object_or_404(Friendship, user=friend, friend=request.user, is_accepted=False)
    
    # 接受好友请求
    friendship.is_accepted = True
    friendship.save()
    
    # 创建反向好友关系
    Friendship.objects.create(user=request.user, friend=friend, is_accepted=True)
    
    # 创建通知
    Notification.objects.create(
        user=friend,
        message=f'{request.user.username} 接受了你的好友请求',
        notification_type='system',
        related_user=request.user
    )
    
    messages.success(request, f'已添加 {friend.username} 为好友')
    return redirect('chat:home')

@login_required
def reject_friend_request(request, username):
    friend = get_object_or_404(User, username=username)
    friendship = get_object_or_404(Friendship, user=friend, friend=request.user, is_accepted=False)
    friendship.delete()
    
    messages.success(request, '已拒绝好友请求')
    return redirect('chat:home')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'chat/notifications.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def friends_list(request):
    """好友列表页面"""
    # 获取已接受的好友关系
    friendships = Friendship.objects.filter(user=request.user, is_accepted=True)
    friends = [friendship.friend for friendship in friendships]
    
    # 获取待处理的好友请求（别人发给我的）
    pending_requests = Friendship.objects.filter(friend=request.user, is_accepted=False)
    
    # 获取我发出的待处理请求
    sent_requests = Friendship.objects.filter(user=request.user, is_accepted=False)
    
    # 搜索用户功能 - 支持用户名和好友代码
    search_query = request.GET.get('search', '')
    search_results = []
    if search_query:
        # 先尝试通过好友代码精确匹配
        try:
            user_by_code = User.objects.get(friend_code=search_query)
            if user_by_code.id != request.user.id:
                search_results = [user_by_code]
        except User.DoesNotExist:
            # 如果好友代码没找到，则通过用户名模糊搜索
            search_results = User.objects.filter(
                username__icontains=search_query
            ).exclude(id=request.user.id)[:10]
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
        'search_query': search_query,
        'search_results': search_results,
    }
    return render(request, 'chat/friends_list.html', context)
