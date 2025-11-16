from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from .forms import UserRegisterForm, UserProfileForm, UsernameChangeForm
from .models import User
from django.utils import timezone
import os
from PIL import Image
import io

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
    
    # 获取用户发布的帖子（使用Topic模型）
    posts = user.topics.all().order_by('-created_at')
    
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

@login_required
def update_background(request):
    """更新用户背景图片视图"""
    if request.method == 'POST':
        try:
            # 处理文件上传
            if 'background' in request.FILES:
                background_file = request.FILES['background']
                
                # 验证文件类型
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                if background_file.content_type not in allowed_types:
                    return JsonResponse({
                        'success': False,
                        'message': '不支持的文件格式，请上传 JPG, PNG 或 GIF 图片'
                    })
                
                # 验证文件大小（最大 5MB）
                if background_file.size > 5 * 1024 * 1024:
                    return JsonResponse({
                        'success': False,
                        'message': '文件大小不能超过 5MB'
                    })
                
                # 保存文件
                request.user.background = background_file
                request.user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '背景图片已更新'
                })
            
            # 处理预设背景
            elif 'preset_background' in request.POST:
                preset = request.POST['preset_background']
                size = request.POST.get('size', '1200x400')  # 获取尺寸参数
                
                # 生成预设背景图片
                background_image = create_preset_background(preset, size)
                if background_image:
                    # 保存图片到内存
                    img_buffer = io.BytesIO()
                    background_image.save(img_buffer, format='JPEG', quality=95)
                    img_buffer.seek(0)
                    
                    # 创建文件对象
                    from django.core.files.base import ContentFile
                    filename = f'preset_{preset}_{size.replace("x", "_")}.jpg'
                    file_content = ContentFile(img_buffer.getvalue(), name=filename)
                    
                    # 更新用户背景
                    request.user.background.save(filename, file_content, save=True)
                    
                    return JsonResponse({
                        'success': True,
                        'message': '预设背景已应用'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': '无效的预设背景'
                    })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': '请选择背景图片或预设'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'保存失败：{str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': '无效的请求方法'
    })

def create_preset_background(preset, size='1200x400'):
    """创建预设背景图片"""
    # 解析尺寸
    try:
        width, height = map(int, size.split('x'))
    except ValueError:
        width, height = 1200, 400  # 默认尺寸
    
    gradients = {
        'gradient1': [(102, 126, 234), (118, 75, 162)],  # 蓝紫渐变
        'gradient2': [(240, 147, 251), (245, 87, 108)],  # 粉红渐变
        'gradient3': [(79, 172, 254), (0, 242, 254)],    # 青蓝渐变
        'gradient4': [(67, 233, 123), (56, 249, 215)],   # 绿青渐变
        'gradient5': [(250, 112, 154), (254, 225, 64)],  # 粉黄渐变
        'gradient6': [(168, 237, 234), (254, 214, 227)], # 青粉渐变
    }
    
    if preset not in gradients:
        return None
    
    # 创建渐变背景
    image = Image.new('RGB', (width, height))
    
    # 创建渐变效果
    color1, color2 = gradients[preset]
    for y in range(height):
        # 计算渐变比例
        ratio = y / height
        # 插值计算颜色
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        
        # 绘制这一行
        for x in range(width):
            image.putpixel((x, y), (r, g, b))
    
    return image
