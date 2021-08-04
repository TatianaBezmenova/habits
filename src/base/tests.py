import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from .models import Task, DailyTask


class TaskModelTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user_bob = User.objects.create_user('bob', password='qwerty-123')
        self.task = Task.objects.create(
            user=self.user_bob,
            title='test-task',
            date_start=datetime.date(2021, 8, 1),
            date_end=datetime.date(2021, 8, 10)
        )

    def tearDown(self):
        Task.objects.all().delete()
        DailyTask.objects.all().delete()
        User.objects.all().delete()
        super().tearDown()

    def test_task_create(self):
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.title, 'test-task', 'Проверка наименования')
        self.assertEqual(task.date_start, datetime.date(2021, 8, 1), 'Проверка даты начала')
        self.assertEqual(task.date_end, datetime.date(2021, 8, 10), 'Проверка даты окончания')
        self.assertFalse(task.complete, 'Проверка задачи на незавершенность')

    def test_task_save(self):
        task = Task.objects.get(id=self.task.id)
        task.title = 'test-task-2'
        task.save()
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.title, 'test-task-2', 'Провекра сохранения изменений по задаче')
        daily_tasks = DailyTask.objects.filter(task=task.id)
        self.assertEqual(len(daily_tasks), 10,
                         'Проверка, что сохранение изменений в основной задачи не привело к созданию новых ежедневных задач')

    def test_task_delete(self):
        task = Task.objects.get(id=self.task.id)
        task.delete()
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=self.task.id)

        daily_tasks = DailyTask.objects.filter(task=self.task.id)
        self.assertFalse(daily_tasks, 'Проверка, что при удалении основной задачи удаляются и ежедневные задачи')


class DailyTaskModelTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user_bob = User.objects.create_user('bob', password='qwerty-123')
        self.task = Task.objects.create(
            user=self.user_bob,
            title='test-task',
            date_start=datetime.date(2021, 8, 1),
            date_end=datetime.date(2021, 8, 10)
        )

    def tearDown(self):
        Task.objects.all().delete()
        DailyTask.objects.all().delete()
        User.objects.all().delete()
        super().tearDown()

    def test_daily_tasks_create(self):
        daily_tasks = DailyTask.objects.filter(task=self.task.id)
        self.assertEqual(len(daily_tasks), 10, 'Проверка количества ежедневных задач')

        DailyTask.objects.get(task=self.task.id, date=self.task.date_start)
        DailyTask.objects.get(task=self.task.id, date=self.task.date_end)

        for task in daily_tasks:
            self.assertFalse(task.complete, 'Проверка задач на незавершенность')

    def test_daily_tasks_save(self):
        daily_task = DailyTask.objects.filter(task=self.task.id).all()[0]
        id_ = daily_task.id
        daily_task.complete = True
        daily_task.save()
        daily_task = DailyTask.objects.get(id=id_)
        self.assertTrue(daily_task.complete, 'Проверка сохранения изменений в задаче на день')


class UserViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user_bob = User.objects.create_user('bob', password='qwerty-123')
        self.user_eve = User.objects.create_user('eve', password='qwerty-123')
        self.superuser = User.objects.create_superuser('ann', password='qwerty-123')

    def tearDown(self):
        User.objects.all().delete()
        super().tearDown()

    def test_user_can_see_login_page(self):
        login_url = reverse('login')
        self.client.logout()
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, HttpResponse.status_code,
                         'Провекра что страница для входа доступна анон.пользователю')

        self.client.force_login(self.user_bob)
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code,
                         'Проверка что для залогиненого пользователя страница входа не доступна')

    def test_login(self):
        login_url = reverse('login')
        redirect_url = reverse('tasks')
        self.client.logout()
        response = self.client.post(login_url, data={'username': 'bob', 'password': 'qwerty-123'})
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code,
                         'Проверка входа')

        self.assertEqual(response.headers['location'], redirect_url,
                         'Проверка что после входа редикект на верную страницу')

        self.client.logout()
        response = self.client.post(login_url, data={'username': 'bob', 'password': 'qwerty-1234'})
        self.assertEqual(response.status_code, HttpResponse.status_code, 'Проверка если ввели неверный логин/пароль')
        self.assertIn('Пожалуйста, введите правильные имя пользователя и пароль', response.content.decode())

    def test_logout(self):
        logout_url = reverse('logout')
        redirect_url = reverse('login')
        self.client.force_login(self.user_bob)
        self.assertIn('_auth_user_id', self.client.session, 'Проверка что пользователь залогинен')

        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        self.assertEqual(response.headers['location'], redirect_url)
        self.assertNotIn('_auth_user_id', self.client.session, 'Проверка что пользователь разлогинен')

    def test_user_can_see_tasks_page(self):
        url = reverse('tasks')
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code,
                         'Провекра что страница задач не доступна анон.пользователю')

        self.client.force_login(self.user_bob)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code,
                         'Провекра что страница задач доступна залогиненому пользователю')

        self.client.force_login(self.user_eve)
        response = self.client.get(url)
        self.assertIn('Нет привычек', response.content.decode(), 'Проверка, что пользователь видит только свои задачи')

    def test_user_tasks_add_page(self):
        add_task_url = reverse('task-create')
        tasks_url = reverse('tasks')
        self.client.logout()
        response = self.client.get(add_task_url)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code,
                         'Провекра что страница задач не доступна анон.пользователю')

        self.client.force_login(self.user_bob)
        response = self.client.get(add_task_url)
        self.assertEqual(response.status_code, HttpResponse.status_code,
                         'Провекра что страница задач доступна залогиненому пользователю')

        correct_content = {
            'user': self.user_bob,
            'title': 'test-task-bob',
            'date_start': datetime.date(2021, 8, 1),
            'date_end': datetime.date(2021, 8, 10)
        }
        response = self.client.post(add_task_url, data=correct_content)
        self.assertEqual(response.headers['location'], tasks_url,
                         'Проверка что после добавления задачи пользователь был перенаправлен')
        self.assertTrue(Task.objects.filter(title='test-task-bob').exists(),
                        'Проверка что данные о новой задаче сохранились')
