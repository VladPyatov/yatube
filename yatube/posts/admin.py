from django.contrib import admin

from posts.models import Group, Post, Comment, Follow
from yatube.settings import EMPTY_VALUE


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Fields to display
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    # Editable fields
    list_editable = ('group',)
    # Field where search will be held
    search_fields = ('text',)
    # Filter fields
    list_filter = ('pub_date',)

    empty_value_display = EMPTY_VALUE


admin.site.register(Group)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Fields to display
    list_display = ('pk', 'post', 'author', 'text')
    # Field where search will be held
    search_fields = ('text',)
    # Filter fields
    list_filter = ('created',)

    empty_value_display = EMPTY_VALUE


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    # Fields to display
    list_display = ('user', 'author')
    # Field where search will be held
    search_fields = ('user',)
    empty_value_display = EMPTY_VALUE
