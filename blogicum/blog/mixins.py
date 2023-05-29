from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy


from .models import Comment, Post


class PostMixin:
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


class CommentMixin:
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
            args=(self.kwargs['id'],)
        )
