from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from users.models import Profile
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

class SearchView(ListView):
    model=Post
    template_name = 'blog/search_bar.htm'
    context_object_name = 'posts'
    ordering = ['-date_published']
    paginate_by=5

    def get_queryset(self):
        if self.request.method == 'GET':
            queries=self.request.GET.get('search')
            if queries:
                queries=queries.split(" ")
                queryset=[]
                for q in queries:
                    posts=Post.objects.all().filter(Q(title__icontains=q) | Q(content__icontains=q)).distinct()
                    for post in posts:
                        queryset.append(post)
            else:
                queryset=Post.objects.none()
            return list(set(queryset))

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.htm'
    context_object_name = 'posts'
    ordering = ['-date_published']
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.htm'
    context_object_name = 'posts'
    ordering = ['-date_published']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_published')

    

class PostDetailView(DetailView):
    model = Post
    template_name='blog/post_detail.htm'

    def get_context_data(self, *args, **kwargs): 
        context = super().get_context_data(*args, **kwargs)
        post=get_object_or_404(Post,pk=self.kwargs.get('pk'))
        
        num_likes = post.likes.count

        is_liked=False
        if post.likes.filter(id=self.request.user.id).exists():
            is_liked=True
        context['is_liked']=is_liked
        context['num_likes']=num_likes
        return context 

def LikeView(request):
    post = get_object_or_404(Post,id=request.POST.get('post_id'))
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(post.get_absolute_url())

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_form.htm'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_form.htm'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.htm'

    def test_func(self):
        post = self.get_object()
        if post.author == self.request.user:
            return True
        return False


def about(request):
    context = {
        'title': 'About'
    }
    return render(request, 'blog/about.htm', context)


def get_blog_search(query=None):
    queryset = []
    queries = query.split(" ")
    for q in queries:
        posts = Post.objects.all().filter(title=q)

        for post in posts:
            queryset.append(post)
    return list(set(queryset))
