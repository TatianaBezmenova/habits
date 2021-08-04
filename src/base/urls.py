from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import TaskList, TaskCreate, TaskUpdate, TaskDelete, CustomLoginView, RegisterPage, \
    DailyTaskList, test_save

urlpatterns = [
    path('', TaskList.as_view(), name='tasks'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>', TaskDelete.as_view(), name='task-delete'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),
    path('task/<int:pk>', DailyTaskList.as_view(), name='task'),
    path('test/<int:pk>', test_save, name='test'),
]
