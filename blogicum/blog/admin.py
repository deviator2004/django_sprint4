from django.contrib import admin

from .models import Location, Category, Post, Comment

admin.site.empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'is_published',
        'pub_date',
        'location',
        'category',
    )
    list_editable = (
        'is_published',
        'pub_date',
        'location',
        'category',
    )
    search_fields = ('title', 'text')
    list_filter = ('author', 'location', 'category')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'description', 'slug')
    list_editable = ('is_published',)
    search_fields = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'post', 'author')
