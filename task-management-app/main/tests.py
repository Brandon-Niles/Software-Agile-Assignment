from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task
from django.core.exceptions import ValidationError

class TaskModelTest(TestCase):
    def test_create_task(self):
        task = Task.objects.create(
            title="System Update",
            platform="Linux",
            location="London",
            status="Pending",
            start_time="2024-01-01 10:00",
            end_time="2024-01-01 12:00",
            retries=1
        )
        self.assertEqual(str(task), "System Update - London - Pending")

class TaskViewTest(TestCase):
    def setUp(self):
        self.admin, _ = User.objects.get_or_create(username='admin')
        # ensure admin properties and password
        self.admin.set_password('adminpass')
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()

        self.user, _ = User.objects.get_or_create(username='user')
        self.user.set_password('userpass')
        self.user.is_staff = False
        self.user.is_superuser = False
        self.user.save()
        for i in range(60):
            Task.objects.create(
                title=f"Task {i}",
                platform="Linux",
                location="London",
                status="Pending",
                start_time="2024-01-01 10:00",
                end_time="2024-01-01 12:00",
                retries=i
            )

    def test_task_list_requires_login(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_task_list_admin(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task Management System")
        self.assertContains(response, "Task 0")
        self.assertContains(response, "Task 49")
        self.assertNotContains(response, "Task 50")  # Pagination: only 50 per page

    def test_task_list_pagination(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('task_list') + '?page=2')
        self.assertContains(response, "Task 50")
        self.assertContains(response, "Task 59")

    def test_search(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('task_list'), {'search': 'Task 1'})
        self.assertContains(response, "Task 1")
        self.assertNotContains(response, "Task 2")

    def test_ajax_search(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(
            reverse('task_list'),
            {'search': 'Task 1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertIn('Task 1', response.json()['html'])

    def test_add_task_admin(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('add_task'), {
            'title': 'New Task',
            'platform': 'Windows',
            'location': 'NY',
            'status': 'Running',
            'start_time': '2024-01-01 09:00',
            'end_time': '2024-01-01 10:00',
            'retries': 0
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_add_task_non_admin(self):
        self.client.login(username='user', password='userpass')
        response = self.client.post(reverse('add_task'), {
            'title': 'Should Not Work',
            'platform': 'Windows',
            'location': 'NY',
            'status': 'Running',
            'start_time': '2024-01-01 09:00',
            'end_time': '2024-01-01 10:00',
            'retries': 0
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(title='Should Not Work').exists())

    def test_edit_task_admin(self):
        self.client.login(username='admin', password='adminpass')
        task = Task.objects.first()
        response = self.client.post(reverse('edit_task', args=[task.id]), {
            'title': 'Edited Task',
            'platform': task.platform,
            'location': task.location,
            'status': task.status,
            'start_time': task.start_time,
            'end_time': task.end_time,
            'retries': task.retries
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Edited Task')

    def test_edit_task_non_admin(self):
        self.client.login(username='user', password='userpass')
        task = Task.objects.first()
        response = self.client.post(reverse('edit_task', args=[task.id]), {
            'title': 'Should Not Edit',
            'platform': task.platform,
            'location': task.location,
            'status': task.status,
            'start_time': task.start_time,
            'end_time': task.end_time,
            'retries': task.retries
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertNotEqual(task.title, 'Should Not Edit')

    def test_invalid_retries_validation(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('add_task'), {
            'title': 'Invalid Retries',
            'platform': 'Windows',
            'location': 'NY',
            'status': 'Running',
            'start_time': '2024-01-01 09:00',
            'end_time': '2024-01-01 10:00',
            'retries': -1
        })
        # form invalid -> returns the form page with errors (200)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(title='Invalid Retries').exists())
        self.assertIn('Retries must be zero or positive', response.content.decode())

    def test_invalid_time_format(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('add_task'), {
            'title': 'Bad Time',
            'platform': 'Windows',
            'location': 'NY',
            'status': 'Running',
            'start_time': 'not-a-date',
            'end_time': '2024/01/01',
            'retries': 0
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(title='Bad Time').exists())
        self.assertIn('Invalid date/time format', response.content.decode())

    def test_end_before_start_validation(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('add_task'), {
            'title': 'End Before Start',
            'platform': 'Windows',
            'location': 'NY',
            'status': 'Running',
            'start_time': '2024-01-01 10:00',
            'end_time': '2024-01-01 09:00',
            'retries': 0
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(title='End Before Start').exists())
        self.assertIn('End time must be the same or after start time', response.content.decode())

    def test_model_full_clean_raises(self):
        task = Task(
            title='Model Check',
            platform='P',
            location='L',
            status='Pending',
            start_time='2024-01-01 10:00',
            end_time='2024-01-01 09:00',
            retries=0
        )
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_ajax_delete_reduces_counts(self):
        self.client.login(username='admin', password='adminpass')
        total_before = Task.objects.count()
        t = Task.objects.first()
        resp = self.client.post(reverse('delete_task', args=[t.id]), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get('success'))
        self.assertEqual(Task.objects.count(), total_before-1)

    def test_ajax_add_increases_counts(self):
        self.client.login(username='admin', password='adminpass')
        total_before = Task.objects.count()
        resp = self.client.post(reverse('add_task'), {
            'title': 'Ajax Created',
            'platform': 'Web',
            'location': 'Remote',
            'status': 'Pending',
            'start_time': '2024-02-02 10:00',
            'end_time': '2024-02-02 11:00',
            'retries': 0
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # Should return JSON success
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get('success'))
        self.assertEqual(Task.objects.count(), total_before+1)
