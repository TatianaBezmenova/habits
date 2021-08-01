from django.contrib import admin

from .models import Task, DailyTask


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    ordering = ['-create']
    list_display = ['user', 'title', 'complete', 'create']


@admin.register(DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'date', 'complete']
