from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.
@login_required
def inbox(request):
    user= request.user
    messages = Message.get_message(user=user)
    active_direct = None
    directs = None
    page = 'direct'

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=user, recipient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

    context = {'directs': directs, 'active_direct': active_direct, 'messages': messages, 'page': page}

    return render(request, 'inbox.html', context)

@login_required
def Directs(request, username):
    page = 'direct'
    user = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, recipient__username=username)
    directs.update(is_read=True)

    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0
    
    context = {'directs': directs, 'active_direct': active_direct, 'messages': messages, 'page': page}

    return render(request, 'directs.html', context)

@login_required
def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == 'POST':
        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, body)
        return redirect('inbox')
    else:
        pass

@login_required
def UserSearch(request):
    page_type = 'search'
    query = request.GET.get('q')
    context = {'page': page_type}
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Paginator
        paginator = Paginator(users, 8) # display 8 each
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {'users': users_paginator, 'page': page_type}

    return render(request, 'search.html', context)

@login_required
def NewConversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('search-users')
    if from_user != to_user:
        Message.send_message(from_user, to_user, body)
    return redirect('inbox')
