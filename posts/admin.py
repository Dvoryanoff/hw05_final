from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):

    list_display = ("text", "pub_date", "author")

    search_fields = ("text",)

    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'description', 'title', 'slug')
    search_fields = 'description'
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'post', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('author', 'text')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
