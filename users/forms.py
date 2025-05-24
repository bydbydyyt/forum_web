from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱已被注册')
        return email

class UserProfileForm(forms.ModelForm):
    """用户资料编辑表单"""
    class Meta:
        model = User
        fields = ['avatar', 'background', 'bio', 'show_collections']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class UsernameChangeForm(forms.Form):
    """用户名修改表单"""
    new_username = forms.CharField(
        max_length=150,
        required=True,
        label='新用户名',
        help_text='每周只能修改一次用户名'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def clean_new_username(self):
        new_username = self.cleaned_data.get('new_username')
        
        if not self.user.can_change_username():
            raise ValidationError('每周只能修改一次用户名')
            
        if User.objects.filter(username=new_username).exclude(pk=self.user.pk).exists():
            raise ValidationError('该用户名已被使用')
            
        return new_username 