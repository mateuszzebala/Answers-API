from django.contrib import admin
from .models import Book, Category, Image, Task, Video, Audio, Page, UsersForAuthorization
from django.utils.html import format_html
from django.contrib.sessions.models import Session

admin.site.register(Session)



@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'publishing_house', 'category', 'year']
    list_filter = ['category']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'src', 'task', 'show']
    search_fields = ['task__page__book__name', 'task__answer']
    def show(self, obj):

        return format_html(f'<a href="/image/{obj.id}" target="_blank">SHOW</a>')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'page', 'datetime']
    list_filter = ['page__book', 'page__book__category', 'datetime']




@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'src', 'show']

    def show(self, obj):
        return format_html(f'<a href="/video/{obj.id}" target="_blank">SHOW</a>')



@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'src', 'show']

    def show(self, obj):
        return format_html(f'<a href="/audio/{obj.id}" target="_blank">SHOW</a>')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'number', 'have_tasks']


    def have_tasks(self, obj):
        tasks = Task.objects.filter(page=obj)
        if len(tasks) == 0:
            return False
        return True

@admin.register(UsersForAuthorization)
class UsersForAuthorizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'remove_code', 'datetime']
