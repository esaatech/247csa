import uuid
from django.db import models
from django.contrib.auth.models import User

class Interaction(models.Model):
    INTERACTION_TYPES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
    ]
    
    MEDIUM_CHOICES = [
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('chat', 'Chat'),
        ('whatsapp', 'WhatsApp'),
        ('in_person', 'In Person'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity_uuid = models.UUIDField()  # UUID to associate with any entity (e.g., customer)
    type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    medium = models.CharField(max_length=20, choices=MEDIUM_CHOICES)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='microservice_interactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} via {self.get_medium_display()}"
