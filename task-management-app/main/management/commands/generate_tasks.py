from django.core.management.base import BaseCommand
from main.models import Task
from django.contrib.auth.models import User
from main.models import UserProfile
import random
from datetime import datetime, timedelta

TITLES = [
    "System Update", "Security Patch", "Database Backup", "User Sync",
    "Log Rotation", "Disk Cleanup", "Service Restart", "Network Scan",
    "Software Deployment", "Resource Monitoring"
]
PLATFORMS = ['AWS', 'Azure', 'GCP', 'VMware', 'On-Premise']
LOCATIONS = ['London', 'Frankfurt', 'Sydney', 'New York', 'Tokyo']
STATUSES = ['Pending', 'Running', 'Completed', 'Failed', 'Cancelled']

class Command(BaseCommand):
    help = 'Generate 500 realistic system tasks'

    def handle(self, *args, **kwargs):
        Task.objects.all().delete()
        # Ensure sample admin and client users exist
        admin_user, _ = User.objects.get_or_create(username='admin')
        # Always reset seeded admin password to known value for testing
        admin_user.set_password('adminpass')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})

        client_user, _ = User.objects.get_or_create(username='user')
        # Always reset seeded regular user password to known value for testing
        client_user.set_password('userpass')
        client_user.is_staff = False
        client_user.is_superuser = False
        client_user.save()
        UserProfile.objects.get_or_create(user=client_user, defaults={'role': 'client'})
        for _ in range(500):
            start = datetime.now() - timedelta(days=random.randint(0, 30))
            end = start + timedelta(hours=random.randint(1, 48))
            Task.objects.create(
                title=random.choice(TITLES),
                platform=random.choice(PLATFORMS),
                location=random.choice(LOCATIONS),
                status=random.choice(STATUSES),
                start_time=start.strftime("%Y-%m-%d %H:%M"),
                end_time=end.strftime("%Y-%m-%d %H:%M"),
                retries=random.randint(0, 5),
                owner=random.choice([admin_user, client_user])
            )
        self.stdout.write(self.style.SUCCESS('Successfully generated 500 realistic system tasks'))