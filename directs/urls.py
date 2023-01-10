from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name="inbox"),
    path('@<username>', views.Directs, name='directs'),
    path('send', views.SendDirect, name='send-directs'),
    path('new/', views.UserSearch, name='user-searchs'),
    path('new/<username>', views.NewConversation, name='new-message'),


]