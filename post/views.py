from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Tag, Post, Follow, Stream, Like
from django.contrib.auth.decorators import login_required
from .forms import NewPostForm
from userauths.models import Profile
from comment.models import Comment
from comment.forms import CommentForm

# Create your views here.

# main page
@login_required
def index(request):
    page = 'index'
    user = request.user
    all_users = User.objects.all()
    posts = Stream.objects.filter(user=user)
    group_ids = []
    # comment_dict = dict()
    for post in posts:
        group_ids.append(post.post_id)
        # comment_dict[post.post_id] = Comment.objects.filter(post_id=post.post_id).count()
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
    context = {'post_items': post_items, 'all_users': all_users, 'page': page}
    return render(request, 'index.html', context)

# create new post page
@login_required
def NewPost(request):
    page = 'newpost'
    user = request.user.id
    tags_objs = []

    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)

        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tag')
            tags_list = list(tag_form.split(','))

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag) # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#get-or-create
                tags_objs.append(t)

            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user_id=user)
            p.tag.set(tags_objs)
            p.save()
            return redirect('index')

    else:
        form = NewPostForm()

    context = {'form': form, 'page': page}

    return render(request, 'newpost.html', context)

# post details page
def PostDetail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    page = 'post-details'

    # comment
    comments = Comment.objects.filter(post=post).order_by('-date')

    # comment form
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            c = Comment.objects.get(post=comment.post, user=comment.user, body=comment.body, date=comment.date)
            post.comment.add(c)
            return HttpResponseRedirect(reverse('post-details', args=[post_id]))

    else:
        form = CommentForm()

    context = {'post': post, 'form': form, 'comments': comments, 'page': page}

    return render(request, 'post-details.html', context)
    # Note: if user create comment objects in admin page, these comments will not be added to post.comment

# tags page
@login_required
def tags(request, tag_slug):
    page = 'tags'
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tag=tag).order_by('-posted')
    context = {'posts': posts, 'tag': tag, 'page': page}

    return render(request, 'tags.html', context)

# like post in index.html
@login_required
def like_index(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Like.objects.filter(user=user, post=post).count()

    if not liked:
        liked = Like.objects.create(user=user, post=post)
        current_likes += 1

    else:
        liked = Like.objects.filter(user=user, post=post).delete()
        current_likes -= 1

    post.likes = current_likes
    post.save()
    
    return HttpResponseRedirect(reverse('index'))
    # return HttpResponseRedirect(reverse('post-details', args=[post_id]))

# like post in post-details.html
@login_required
def like_post(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Like.objects.filter(user=user, post=post).count()

    if not liked:
        liked = Like.objects.create(user=user, post=post)
        current_likes += 1

    else:
        liked = Like.objects.filter(user=user, post=post).delete()
        current_likes -= 1

    post.likes = current_likes
    post.save()
    
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))

# favourite post in index.html
@login_required
def favourite_index(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile, created = Profile.objects.get_or_create(user=user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)

    return HttpResponseRedirect(reverse('index'))

# favourite post in post-details.html
@login_required
def favourite_post(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile, created = Profile.objects.get_or_create(user=user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)

    return HttpResponseRedirect(reverse('post-details', args=[post_id]))