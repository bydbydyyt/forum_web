from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_list, name='home'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/create/', views.topic_create, name='create_topic'),
    path('topic/<int:topic_id>/reply/', views.reply_create, name='reply_create'),
] 