from django.db import models



class Task(models.Model):
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    platform = models.CharField(max_length=50)
    retries = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.location} - {self.status}"
