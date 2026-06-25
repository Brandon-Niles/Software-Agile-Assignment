from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('client', 'Client')], default='client')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Task(models.Model):
    title = models.CharField(max_length=100, default="System Update")
    platform = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Running', 'Running'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100, null=True, blank=True)
    retries = models.IntegerField(default=0)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def _parse_time_value(self, value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        for fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValidationError('Invalid date/time format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM')

    def clean(self):
        if self.retries is not None and self.retries < 0:
            raise ValidationError({'retries': 'Retries must be zero or positive'})
        start = self._parse_time_value(self.start_time)
        end = self._parse_time_value(self.end_time)
        if start and end and end < start:
            raise ValidationError({'end_time': 'End time must be the same or after start time.'})

    def __str__(self):
        return f"{self.title} - {self.location} - {self.status}"
