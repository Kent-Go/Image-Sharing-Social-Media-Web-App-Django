from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Profile
from post.models import Post, Follow, Stream
from django.urls import resolve, reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.db import transaction
from .forms import EditProfileForm, UserRegisterForm
from django.contrib import messages

# Create your views here.
def userProfile(request, username):
    page = 'profile'
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name # used for resolving URL paths to the corresponding view functions

    if url_name == 'profile':
        # display posts
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        # display favourite posts
        posts = profile.favourite.all()

    #pagination: https://docs.djangoproject.com/en/4.1/topics/pagination/#using-paginator-in-a-view-function
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    #track profile
    post_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count() # get Follow object which the follower is the request.user
    followers_count = Follow.objects.filter(following=user).count() # get Follow object which the following is the request.user

    #follow status
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    context = {
        'posts_paginator': posts_paginator,
        'profile': profile, 'posts': posts,
        'url_name': url_name,
        'post_count': post_count,
        'following_count': following_count,
        'followers_count': followers_count,
        'follow_status': follow_status,
        'page': page,
    }

    return render(request, 'profile.html', context)

@login_required
def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
        else:
            posts = Post.objects.filter(user=following)[:10]

            with transaction.atomic(): # database transaction to maintain data integrity
                # atomic allows us to create a block of code within 
                # which the atomicity on the database is guaranteed. 
                # If the block of code is successfully completed, 
                # the changes are committed to the database. If there is an exception, the changes are rolled back.
                for post in posts:
                    stream = Stream(post=post, user=user, date=post.posted, following=following)
                    stream.save()
        
        return HttpResponseRedirect(reverse('profile', args=[username]))
    
    except User.DoesNotExist:
       return HttpResponseRedirect(reverse('profile', args=[username]))

def editProfile(request, username):
    page = 'edit-profile'
    user = request.user.id
    profile = Profile.objects.get(user__id=user)
    form = EditProfileForm(instance=profile)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile.image = form.cleaned_data.get('image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.bio = form.cleaned_data.get('bio')
            profile.save()
            return redirect('profile', profile.user.username)

    context = {
        'form': form,
        'page': page,
    }

    return render(request, 'edit-profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            new_user = form.save()

            # print success message
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}, Your account was created successfully!')

            # log user in automatically
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, new_user)

            return redirect('edit-profile', username)
    elif request.user.is_authenticated:
        return redirect('index')
    else:
        form = UserRegisterForm()

    context = {'form': form}

    return render(request, 'sign-up.html', context)