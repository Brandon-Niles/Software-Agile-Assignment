import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Task

# Create users
User.objects.all().delete()
Task.objects.all().delete()
admin = User.objects.create_user(username='admin', password='adminpass', is_superuser=True)
user = User.objects.create_user(username='user', password='userpass')

c = Client()
logged_in = c.login(username='user', password='userpass')
print('logged in:', logged_in)
resp = c.post('/tasks/add/', {
    'title': 'Should Not Work',
    'platform': 'Windows',
    'location': 'NY',
    'status': 'Running',
    'start_time': '2024-01-01 09:00',
    'end_time': '2024-01-01 10:00',
    'retries': 0
})
print('response status_code:', resp.status_code)
print('tasks with title count:', Task.objects.filter(title='Should Not Work').count())
for t in Task.objects.filter(title='Should Not Work'):
    print('Task:', t.title, 'owner:', getattr(t.owner, 'username', None))
