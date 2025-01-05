from django.db import models
from django.contrib.auth.models import User

class Assistant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Instruction(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name='instructions')
    content = models.TextField()
    order = models.IntegerField()

class Document(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='assistant_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Channel(models.Model):
    """For integrations/sources"""
    NAME_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('messenger', 'Facebook Messenger'),
        ('instagram', 'Instagram DM'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('sms', 'SMS'),
        ('voice', 'Voice'),
    ]
    
    name = models.CharField(max_length=50, choices=NAME_CHOICES)
    display_name = models.CharField(max_length=255)
    description = models.TextField()

class Integration(models.Model):
    """Connection between Assistant and Channel"""
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name='integrations')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    config = models.JSONField()  # Store channel-specific configuration
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
