from django.urls import path
from django.conf.urls import url
from .views import (
    PostListView, 
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    SearchView,
    LikeView,
    )
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name="blog-home"),
    path('search/$/',SearchView.as_view(),name='search-bar'),
    path('post/<int:pk>/',PostDetailView.as_view(),name='post-detail'),
    path('post/new/',PostCreateView.as_view(),name='post-create'),
    path('post/<int:pk>/update',PostUpdateView.as_view(),name='post-update'),
    path('post/<int:pk>/delete',PostDeleteView.as_view(),name='post-delete'),
    path('user/<str:username>/',UserPostListView.as_view(),name='user-posts'),
    path(r'^like/$/',LikeView,name='like-post'),
    path('about/', views.about, name='blog-about'),
]
