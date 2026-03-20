from django.db import models
from django.utils import timezone

class Worker(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['worker', '-entry_time']),
        ]
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)

    def get_duration(self):
        if self.entry_time:
            # Use current time if worker hasn't punched out yet
            end_time = self.exit_time or timezone.now()
            duration = end_time - self.entry_time
            
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            return f"{hours}h {minutes}m {seconds}s"
        return "0s"

    def __str__(self):
        return f"{self.worker.name} - {self.entry_time.strftime('%Y-%m-%d')}"