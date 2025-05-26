from django.db import models
from django.conf import settings

class Assistant(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assistants'
    )
    # ... other fields ...
