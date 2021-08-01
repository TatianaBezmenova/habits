import datetime
import sys

from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    complete = models.BooleanField(default=False, verbose_name='Завершена')
    create = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField(verbose_name='Дата начала')
    date_end = models.DateField(verbose_name='Дата окончания')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['complete']
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class DailyTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Задача')
    date = models.DateField(verbose_name='Дата')
    complete = models.BooleanField(default=False, verbose_name='Выполнено')

    def __str__(self):
        return self.task.title

    class Meta:
        verbose_name = 'Задача на день'
        verbose_name_plural = 'Задачи на день'


def create_daily_tasks(sender, instance, created, **kwargs):
    daily_tasks = DailyTask.objects.filter(task=instance)
    count = (instance.date_end - instance.date_start).days

    if count >= 0 and len(daily_tasks) == 0:
        for i in range(0, count + 1):
            date = instance.date_start + datetime.timedelta(days=i)
            DailyTask.objects.create(task=instance, date=date)


signals.post_save.connect(create_daily_tasks, sender=Task)
