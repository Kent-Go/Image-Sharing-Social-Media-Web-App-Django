from django.urls import path
from post import views

urlpatterns = [
    path('', views.index, name='index'),
    path('newpost/', views.NewPost, name='newpost'),
    path('post/<uuid:post_id>/', views.PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>/', views.tags, name='tags'),
    path('post/<uuid:post_id>/like_index', views.like_index, name='like_index'),
    # path('post/<uuid:post_id>/like/', views.like, name='like'),
    path('post/<uuid:post_id>/like_post', views.like_post, name='like_post'),
    path('post/<uuid:post_id>/favourite_index', views.favourite_index, name='favourite_index'),
    path('post/<uuid:post_id>/favourite_post', views.favourite_post, name='favourite_post'),
]