import datetime as dt

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy

from .models import Post, Category, Comment, User
from .forms import PostForm, CommentForm
from .mixins import CommentMixin, PostMixin


PAG = 10

now = dt.datetime.now()


def get_query():
    query = Post.objects.select_related(
        'author',
        'location',
        'category'
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    return query


class PostListView(ListView):
    queryset = get_query().filter(
        pub_date__lt=now,
        is_published=True,
        category__is_published=True
    )
    paginate_by = PAG
    template_name = 'blog/index.html'


class CategoryListView(ListView):
    model = Post
    paginate_by = PAG
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        posts = get_query().filter(
            category=self.category,
            pub_date__lt=now,
            is_published=True
        )
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(ListView):
    model = Post
    paginate_by = PAG
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user == self.author:
            posts = get_query().filter(author=self.author)
        else:
            posts = get_query().filter(
                author=self.author,
                pub_date__lt=now,
                is_published=True,
                category__is_published=True
            )
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


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):

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

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            args=(self.kwargs['id'],)
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass
