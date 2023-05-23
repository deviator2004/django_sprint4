import datetime as dt

from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from .models import Post, Category


def index(request):
    template = 'blog/index.html'
    now = dt.datetime.now()
    post_list = Post.objects.select_related(
        'location', 'category', 'author'
    ).filter(
        pub_date__lt=now,
        is_published=True,
        category__is_published=True
    )[:5]
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    now = dt.datetime.now()
    posts = Post.objects.select_related(
        'author', 'location', 'category'
    ).exclude(
        Q(pub_date__gt=now) | Q(is_published=False)
        | Q(category__is_published=False)
    )
    post = get_object_or_404(posts, pk=id)
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    now = dt.datetime.now()
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    post_list = Post.objects.select_related(
        'location', 'category', 'author'
    ).filter(
        is_published=True,
        category__slug=category_slug,
        pub_date__lt=now
    )
    context = {'category': category, 'post_list': post_list}
    return render(request, template, context)
