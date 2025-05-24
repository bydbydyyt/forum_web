from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Topic, Reply
from .forms import TopicForm, ReplyForm

def forum_list(request):
    topics = Topic.objects.all().order_by('-created_at')
    return render(request, 'forum/forum_list.html', {'topics': topics})

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    replies = topic.replies.all().order_by('created_at')
    return render(request, 'forum/topic_detail.html', {
        'topic': topic,
        'replies': replies
    })

@login_required
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            messages.success(request, '主题创建成功！')
            return redirect('forum:topic_detail', topic_id=topic.id)
    else:
        form = TopicForm()
    return render(request, 'forum/topic_form.html', {'form': form})

@login_required
def reply_create(request, topic_id):
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
