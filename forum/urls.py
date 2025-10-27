from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_list, name='forum_list'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/create/', views.topic_create, name='topic_create'),
    path('topic/<int:topic_id>/reply/', views.reply_create, name='reply_create'),
    path('topic/<int:topic_id>/toggle-pin/', views.toggle_topic_pin, name='toggle_topic_pin'),
    path('topic/<int:topic_id>/toggle-essence/', views.toggle_topic_essence, name='toggle_topic_essence'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
]