from django.db import models
from django.utils import timezone

class Worker(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)

    def get_duration(self):
        """Calculates total hours worked in a session."""
        if self.entry_time and self.exit_time:
            duration = self.exit_time - self.entry_time
            # Converts timedelta to total hours (e.g., 8.5 hours)
            return round(duration.total_seconds() / 3600, 2)
        return 0

    def __str__(self):
        return f"{self.worker.name} - {self.entry_time.strftime('%Y-%m-%d')}"