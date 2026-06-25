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

    def __str__(self):
        return f"{self.title} - {self.location} - {self.status}"

    def clean(self):
        # Validate retries
        if self.retries is not None and self.retries < 0:
            raise ValidationError({'retries': 'Retries must be zero or positive'})

        # Validate start_time and end_time formats and ordering
        def parse_time(value, field_name):
            if value is None or value == '':
                raise ValidationError({field_name: 'This field cannot be empty.'})
            formats = ['%Y-%m-%d %H:%M', '%Y-%m-%d']
            for f in formats:
                try:
                    return datetime.strptime(value, f)
                except Exception:
                    continue
            raise ValidationError({field_name: 'Invalid date/time format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM'})

        # start_time must be present and parseable
        start_dt = None
        try:
            start_dt = parse_time(self.start_time, 'start_time')
        except ValidationError as e:
            raise e

        # end_time is optional but, if provided, must parse and be >= start_time
        if self.end_time:
            try:
                end_dt = parse_time(self.end_time, 'end_time')
            except ValidationError as e:
                raise e
            if end_dt < start_dt:
                raise ValidationError({'end_time': 'End time must be the same or after start time.'})
