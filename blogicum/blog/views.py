import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()
now = dt.datetime.now()


class PostListView(ListView):
    query = Post.objects.annotate(comment_count=Count('comments')).all()
    queryset = query.select_related(
        'author',
        'location',
        'category',
    ).filter(
        pub_date__lt=now,
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')
    paginate_by = 10
    template_name = 'blog/index.html'


class CategoryListView(ListView):
    query = Post.objects.annotate(comment_count=Count('comments')).all()
    model = Post
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        posts = Post.objects.select_related(
            'author',
            'location',
            'category',
        ).annotate(
            comment_count=Count('comments')
        ).filter(
            category=self.category,
            pub_date__lt=now,
            is_published=True
        ).order_by('-pub_date')
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        posts = Post.objects.select_related(
            'author',
            'location',
            'category',
        ).annotate(
            comment_count=Count('comments')
        ).filter(author=self.author).order_by('-pub_date')
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    fields = ('first_name', 'last_name', 'username', 'email')
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:edit_profile')

    def get_object(self, *args, **kwargs):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(User, username=request.user)
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        url = reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )
        return url


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['id'])
        if instance.author != request.user:
            return redirect(
                'blog:post_detail', id=instance.id
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['id'])
        if instance.author != request.user:
            return redirect(
                'blog:post_detail', id=instance.id
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )
        return url


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comments.select_related('author'))
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    comment = None

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Post, pk=kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.comment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.object.post.id}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            return redirect(
                'blog:post_detail', id=instance.post.id
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.object.post.id}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            return redirect(
                'blog:post_detail', id=instance.post.id
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.object.post.id}
        )
