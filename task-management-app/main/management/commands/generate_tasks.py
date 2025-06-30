from django.core.management.base import BaseCommand
from main.models import Task
import random
from datetime import datetime, timedelta

TITLES = [
    "System Update", "Security Patch", "Database Backup", "User Sync",
    "Log Rotation", "Disk Cleanup", "Service Restart", "Network Scan",
    "Software Deployment", "Resource Monitoring"
]
PLATFORMS = ['Windows', 'Linux', 'macOS', 'Azure', 'AWS']
LOCATIONS = ['London', 'Frankfurt', 'Sydney', 'New York', 'Tokyo']
STATUSES = ['Pending', 'Running', 'Completed', 'Failed', 'Cancelled']

class Command(BaseCommand):
    help = 'Generate 100 realistic system tasks'

    def handle(self, *args, **kwargs):
        Task.objects.all().delete()
        for _ in range(100):
            start = datetime.now() - timedelta(days=random.randint(0, 30))
            end = start + timedelta(hours=random.randint(1, 48))
            Task.objects.create(
                title=random.choice(TITLES),
                platform=random.choice(PLATFORMS),
                location=random.choice(LOCATIONS),
                status=random.choice(STATUSES),
                start_time=start.strftime("%Y-%m-%d %H:%M"),
                end_time=end.strftime("%Y-%m-%d %H:%M"),
                retries=random.randint(0, 5)
            )
        self.stdout.write(self.style.SUCCESS('Successfully generated 100 realistic system tasks'))