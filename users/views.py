from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegisterForm, UserProfileForm, UsernameChangeForm
from .models import User
from django.utils import timezone

def register(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('users:profile', username=user.username)
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request, username):
    """用户个人资料视图"""
    user = get_object_or_404(User, username=username)
    is_self = request.user == user
    
    # 获取用户发布的帖子
    posts = user.posts.all().order_by('-created_at')
    
    context = {
        'profile_user': user,
        'is_self': is_self,
        'posts': posts,
    }
    return render(request, 'users/profile.html', context)

@login_required
def settings(request):
    """用户设置视图"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新！')
            return redirect('users:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/settings.html', {'form': form})

@login_required
def change_username(request):
    """修改用户名视图"""
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST, user=request.user)
        if form.is_valid():
            new_username = form.cleaned_data['new_username']
            success, message = request.user.change_username(new_username)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('users:profile', username=new_username)
    else:
        form = UsernameChangeForm(user=request.user)
    
    # 计算下次可以修改的时间
    if request.user.last_username_change:
        next_change_date = request.user.last_username_change + timezone.timedelta(days=7)
        days_remaining = (next_change_date - timezone.now()).days
    else:
        days_remaining = 0
    
    context = {
        'form': form,
        'days_remaining': days_remaining,
        'username_changes_count': request.user.username_changes_count,
    }
    return render(request, 'users/change_username.html', context)
