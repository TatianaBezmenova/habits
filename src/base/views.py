import logging
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from base.models import Task, DailyTask

logger = logging.getLogger(__name__)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user).order_by('-create')
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)
        context['search_input'] = search_input
        return context


class DailyTaskList(LoginRequiredMixin, ListView):
    model = DailyTask
    context_object_name = 'daily_tasks'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        task = Task.objects.get(id=self.kwargs['pk'])
        context['daily_tasks'] = DailyTask.objects.filter(task=task)
        context['task'] = task
        return context


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'date_start', 'date_end']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        logger.info('Пользователь %s создал новую цель: %s', self.request.user, form.cleaned_data['title'])
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        logger.info('Пользователь %s изменил цель: %s', self.request.user, form.cleaned_data['title'])
        form.instance.user = self.request.user
        return super(TaskUpdate, self).form_valid(form)


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def delete(self, request, *args, **kwargs):
        task = Task.objects.get(id=kwargs['pk'])
        logger.info('Пользователь %s удалил цель: %s', request.user, task.title)
        return super(TaskDelete, self).delete(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

    def form_valid(self, form):
        logger.info('Пользователь %s вошел в аккаунт', form.cleaned_data['username'])
        return super(CustomLoginView, self).form_valid(form)

    def form_invalid(self, form):
        logger.warning('Неуспешная попытка входа в аккаунт пользователя %s', form.cleaned_data['username'])
        return super(CustomLoginView, self).form_invalid(form)


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        logger.info('Зарегистрирован новый пользователь %s ', form.cleaned_data['username'])
        return super(RegisterPage, self).form_valid(form)

    def form_invalid(self, form):
        logger.warning('Неуспешная попытка регистрации пользователя %s', form.cleaned_data['username'])
        return super(RegisterPage, self).form_invalid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


def daily_tasks_save(request, pk):
    checks = request.POST.getlist('check')
    checks = list(map(int, checks))
    daily_tasks = DailyTask.objects.filter(task__id=pk)

    for task in daily_tasks:
        if task.id in checks:
            task.complete = True
        else:
            task.complete = False
        task.save()

    return redirect('tasks')
