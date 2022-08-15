"""
View functions for Posts app
"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User, Follow
from yatube.settings import POSTS_PER_PAGE


def index(request):
    """Main page"""
    template = 'posts/index.html'

    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'description': 'Это главная страница проекта Yatube',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Groups posts page"""
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'description': 'Информация о группах проекта Yatube',
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Profile page"""
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author
                                          ).count() != 0
    else:
        following = False
    context = {
        'description': 'Информация о пользователе',
        'author': author,
        'page_obj': page_obj,
        'total_count': post_list.count(),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Post page"""
    post = Post.objects.get(pk=post_id)
    preview = post.text[:30]

    form = CommentForm()
    context = {
        'description': 'Информация о посте',
        'preview': preview,
        'post': post,
        'total_count': post.author.posts.count(),
        'form': form,
        'comments': post.comments.all(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Create post page"""
    author = User.objects.get(username=request.user)
    post = Post(author=author)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if request.POST and form.is_valid():
        form.save()
        return redirect(f'/profile/{request.user}/')

    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Edit post page"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(f'/posts/{post_id}/')
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if request.POST and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    authors = Follow.objects.filter(user=request.user).values('author')
    post_list = Post.objects.filter(author__in=authors)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'description': 'Это cтраница с подписками',
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    already_follower = Follow.objects.filter(user=request.user,
                                             author=author).count()
    if request.user != author and not already_follower:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
