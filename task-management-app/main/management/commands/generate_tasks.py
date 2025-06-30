from django.core.management.base import BaseCommand
from main.models import Task
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generate demo tasks'

    def handle(self, *args, **kwargs):
        locations = [
            "Frankfurt, Germany", "London, UK", "Mumbai, India", "Tokyo, Japan", "New York, USA",
            "Paris, France", "Sydney, Australia", "Singapore", "Dublin, Ireland", "San Francisco, USA"
        ]
        platforms = ["AWS", "Azure", "GCP", "On-prem"]
        statuses = ["Running", "Pending", "Completed", "Failed"]

        Task.objects.all().delete()  # Optional: clear existing tasks

        for i in range(1, 21):
            start_time = timezone.now() - timezone.timedelta(days=random.randint(0, 30))
            end_time = start_time + timezone.timedelta(hours=random.randint(1, 5))
            status = random.choice(statuses)
            Task.objects.create(
                location=random.choice(locations),
                status=status,
                start_time=start_time,
                end_time=end_time if status in ["Completed", "Failed"] else None,
                platform=random.choice(platforms),
                retries=random.randint(0, 3)
            )
        self.stdout.write(self.style.SUCCESS('Successfully generated demo tasks.'))