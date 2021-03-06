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
from .models import Post,Like,Notification
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

    def get_context_data(self, **kwargs):
        context = super(SearchView,self).get_context_data(**kwargs)
        num_likess=[]
        is_likeds=[]
        posts=context['posts']
        for post in posts:
            num_likess.append(post.like_set.all().count())
            user=get_object_or_404(User,id=post.author_id)
            if self.request.user.is_authenticated:
                if Like.objects.filter(user=user,post=post,liked_by=self.request.user).exists():
                    is_likeds.append(True)
                else:
                    is_likeds.append(False)
            else:
                is_likeds.append(False)

        is_likeds_num_likess = zip(is_likeds,num_likess)
        context['is_likeds_num_likess']=is_likeds_num_likess
        return context

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.htm'
    context_object_name = 'posts'
    ordering = ['-date_published']
    paginate_by = 5
    queryset=Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PostListView,self).get_context_data(**kwargs)
        num_likess=[]
        is_likeds=[]
        # posts=Post.objects.all().order_by('-date_published')
        posts=context['posts']
        for post in posts:
            num_likess.append(post.like_set.all().count())
            user=get_object_or_404(User,id=post.author_id)
            if self.request.user.is_authenticated:
                if Like.objects.filter(user=user,post=post,liked_by=self.request.user).exists():
                    is_likeds.append(True)
                    # Like.objects.filter(user=user,post=post).delete()
                else:
                    is_likeds.append(False)
                    # Like.objects.create(user=user,post=post)
            else:
                is_likeds.append(False)

            # num_likess.append(post.likes.count)
            # if post.likes.filter(id=self.request.user.id).exists():
            #     is_likeds.append(True)
            # else:
            #     is_likeds.append(False)

        is_likeds_num_likess = zip(is_likeds,num_likess)
        context['is_likeds_num_likess']=is_likeds_num_likess
        return context
    

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.htm'
    context_object_name = 'posts'
    ordering = ['-date_published']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_published')
    
    def get_context_data(self, **kwargs):
        context = super(UserPostListView,self).get_context_data(**kwargs)
        num_likess=[]
        is_likeds=[]
        posts=context['posts']
        for post in posts:
            num_likess.append(post.like_set.all().count())
            user=get_object_or_404(User,id=post.author_id)
            if self.request.user.is_authenticated:
                if Like.objects.filter(user=user,post=post,liked_by=self.request.user).exists():
                    is_likeds.append(True)
                    # Like.objects.filter(user=user,post=post).delete()
                else:
                    is_likeds.append(False)
                    # Like.objects.create(user=user,post=post)
            else:
                is_likeds.append(False)

        is_likeds_num_likess = zip(is_likeds,num_likess)
        context['is_likeds_num_likess']=is_likeds_num_likess
        return context
    

    

class PostDetailView(DetailView):
    model = Post
    template_name='blog/post_detail.htm'
    context_object_name = 'post'

    def get_context_data(self, *args, **kwargs): 
        context = super().get_context_data(*args, **kwargs)
        post=get_object_or_404(Post,pk=self.kwargs.get('pk'))
        user=get_object_or_404(User,id=post.author_id)

        num_likes = post.like_set.all().count()
        is_liked=False
        if self.request.user.is_authenticated and Like.objects.filter(user=user,post=post,liked_by=self.request.user).exists():
            is_liked=True

        # num_likes = post.likes.count

        # is_liked=False
        # if post.likes.filter(id=self.request.user.id).exists():
        #     is_liked=True
        context['is_liked']=is_liked
        context['num_likes']=num_likes
        return context 

def LikeView(request):
    post = get_object_or_404(Post,id=request.POST.get('post_id'))
    user = get_object_or_404(User,id=post.author_id)
    liked_by = request.user

    if Like.objects.filter(user=user,post=post,liked_by=liked_by).exists():
        Like.objects.filter(user=user,post=post,liked_by=liked_by).delete()
    else:
        Like.objects.create(user=user,post=post,liked_by=liked_by)
    return redirect(post.get_absolute_url())

def NotificationDeleteView(request):
    n = get_object_or_404(Notification,id=request.POST.get('notif_id'))
    user=n.user
    n.delete()
    return redirect('notifications-user',username=user.username)

# def NotificationView(request):
#     user=get_object_or_404(User,id=request.kwargs.get('pk'))
#     print(user)
#     n = Notification.objects.filter(user=user)
#     context['notifications']=n
#     return render(request,'blog/notifications.htm',context)

class NotificationView(LoginRequiredMixin, UserPassesTestMixin,ListView):
    model = Notification
    context_object_name = 'notifications'
    template_name = 'blog/notifications.htm'

    def get_queryset(self):
        user = get_object_or_404(User,username=self.kwargs.get('username'))
        return Notification.objects.filter(user=user)
    
    def test_func(self):
        user = get_object_or_404(User,username=self.kwargs.get('username'))
        if self.request.user == user:
            return True
        return False

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
