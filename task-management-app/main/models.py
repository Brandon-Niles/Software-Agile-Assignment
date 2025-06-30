from django.db import models



class Task(models.Model):
    title = models.CharField(max_length=100, default="System Update")
    platform = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100, null=True, blank=True)
    retries = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.location} - {self.status}"
