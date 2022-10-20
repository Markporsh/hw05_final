from django.urls import path
from . import views
from .views import *

app_name = 'posts'

urlpatterns = [
    path('', Home.as_view(), name='homepage'),
    path(
        'group/<group_slug>/',
        GroupPosts.as_view(), name='group_list'
    ),
    path('profile/<str:username>/', Profile.as_view(), name='profile'),
    path('posts/<int:post_id>/', ShowPost.as_view(), name='post_detail'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('posts/<post_id>/edit/', views.post_edit, name='post_update'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
