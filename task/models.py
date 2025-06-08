import uuid
from django.db import models

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_uuid = models.UUIDField()  # UUID to associate with any entity (e.g., customer)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
