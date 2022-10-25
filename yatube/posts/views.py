from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow, User
from .utils import paginate_posts

POST_ON_PAGE = 10


def index(request):
    posts = Post.objects.select_related('group').all()
    page_obj = paginate_posts(request, posts)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)
    posts = group.group_posts.all()
    page_obj = paginate_posts(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(author=author)
    page_obj = paginate_posts(request, posts)
    following = request.user.is_authenticated and author.following.exists()
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
        'username': username,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = Comment.objects.select_related('post').filter(post=posts)
    template = 'posts/post_detail.html'
    context = {
        'posts': posts,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


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
    page_obj = paginate_posts(request, posts_list)
    template = 'posts/follow.html'
    return render(request, template, {'page_obj': page_obj})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            form.save(commit=False).author = request.user
            form.save()
            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect(
            'posts:profile',
            username=username
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    username = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=username).delete()
    return redirect('posts:profile', username=username)
