from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow, User
from .utils import page_create

POST_ON_PAGE = 10


class Home(ListView):
    model = Post
    template_name = 'posts/index.html'
    paginate_by = POST_ON_PAGE

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class GroupPosts(ListView):
    model = Post
    template_name = 'posts/group_list.html'
    context_object_name = 'posts'
    paginate_by = POST_ON_PAGE
    # allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = Group.objects.get(slug=self.kwargs['group_slug'])
        return context

    def get_queryset(self):
        return Post.objects.select_related('group').filter(
            group__slug=self.kwargs['group_slug']
        )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('group').filter(author=author)
    page_obj = page_create(request, posts)
    following = request.user.is_authenticated and author.following.exists()
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
        'username': username,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


class ShowPost(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'posts'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.select_related('post').filter(
            post_id=context['posts']
        )
        context['form'] = CommentForm()
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.save(commit=False).author_id = self.request.user.pk
        form.save()
        return redirect('posts:profile', username=self.request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    template = 'posts/create_post.html'
    is_edit = True
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    elif form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    posts_list = Post.objects.filter(author__id__in=authors)
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'posts/follow.html',
        {'page_obj': page_obj, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect(
            'posts:profile',
            username=username
        )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
