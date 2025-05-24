from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_home, name='home'),
    path('chat/<str:username>/', views.chat_room, name='chat'),
    path('chat/<str:username>/upload/', views.upload_file, name='upload_file'),
    path('friend/request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friend/accept/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend/reject/<str:username>/', views.reject_friend_request, name='reject_friend_request'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
] 