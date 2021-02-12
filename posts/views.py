from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

import yatube.settings as st

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, st.PAGINATOR_PAGE_SIZE)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}

    return render(
        request,
        'index.html',
        context
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_group.all()
    paginator = Paginator(posts, st.PAGINATOR_PAGE_SIZE)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@cache_page(20)
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    post_count = posts.count()
    paginator = Paginator(posts, st.PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'author': author,
               'page': page,
               'paginator': paginator,
               'post_count': post_count}
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    form = CommentForm(request.POST or None)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    posts = author.posts.all()
    post_count = posts.count()
    comments = post.comments.all()
    context = {
        'post_count': post_count,
        'post': post,
        'author': author,
        'form': form,
        'comments': comments
    }
    return render(request, 'post.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect("index")

    return render(request, "new.html", {"form": form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if not request.user.id == post.author.id:
        return redirect('post', post.author, post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)

    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'post': post})

    form.save()
    return redirect('post', post.author, post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, st.PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {
            'posts': posts,
            'paginator': paginator,
            'page': page,
        }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        author=author,
        user=request.user
    ).exists()
    if request.user != author and not following:
        Follow.objects.create(author=author, user=request.user)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    unfollow = Follow.objects.filter(
        author__username=username, user=request.user
    )
    if unfollow.exists():
        unfollow.delete()
    return redirect('profile', username)


def page_not_found(request, exception):  # noqa
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
