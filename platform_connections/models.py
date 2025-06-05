from django.db import models

# Create your models here.
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from django.db import models
import uuid

class BasePlatformConnection(models.Model):
    agent_id = models.UUIDField()  # No ForeignKey to CSA, fully decoupled
    created_at = models.DateTimeField(auto_now_add=True)
    platform_type = models.CharField(max_length=50)  # Add this field to track platform type
    is_connected = models.BooleanField(default=True)  # Add this to track connection status

    class Meta:
        abstract = True

    @classmethod
    def get_connected_platforms(cls, agent_id):
        """
        Get all platform connections for an agent.
        Returns a dictionary with platform status information.
        """
        platform_status = {
            'website_chat': {
                'is_connected': False,
                'connection_id': None
            },
            'sms': {
                'is_connected': False,
                'connection_id': None
            }
        }
        
        # Check Website Chat
        website_chat = WebsiteChatConnection.objects.filter(agent_id=agent_id).first()
        if website_chat:
            platform_status['website_chat'] = {
                'is_connected': website_chat.is_connected,
                'connection_id': str(website_chat.id)
            }
            
        # Check SMS
        sms = SMSConnection.objects.filter(agent_id=agent_id).first()
        if sms:
            platform_status['sms'] = {
                'is_connected': sms.is_connected,
                'connection_id': str(sms.id)
            }
            
        return platform_status

    def save(self, *args, **kwargs):
        # Set platform_type based on the class name
        self.platform_type = self.__class__.__name__.lower().replace('connection', '')
        super().save(*args, **kwargs)


class WebsiteChatConnection(BasePlatformConnection):
    iframe_token = models.CharField(max_length=100)
    theme = models.CharField(max_length=50, default='dark')
    allowed_domains = models.JSONField(default=list)
    session_tracking = models.JSONField(default=dict)  # Store browser session IDs and their chat sessions
    custom_icon = models.ImageField(upload_to='chat_widget_icons/', null=True, blank=True)  # Add this field for custom icons

    class Meta:
        # Remove any unique constraints
        pass

class SMSConnection(BasePlatformConnection):
    twilio_account_sid = models.CharField(max_length=100)
    twilio_auth_token = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

class PlatformConnection(models.Model):
    PLATFORM_CHOICES = [
        ('website_chat', 'Website Chat'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('messenger', 'Messenger'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('voice', 'Voice'),
    ]

    platform_type = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    config = models.JSONField(default=dict, blank=True)

    # Generic relation to allow linking to different types of objects (e.g., CSA, CRM)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    connected_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_platform_type_display()} connection for {self.connected_object}"

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.UUIDField()  # CSA agent
    platform_type = models.CharField(max_length=50)  # e.g., 'website', 'sms', 'email'
    user_identifier = models.CharField(max_length=255, blank=True, null=True)  # phone, email, or session id
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    HANDLING_CHOICES = [
        ('ai', 'AI'),
        ('human', 'Human'),
    ]
    handling_mode = models.CharField(max_length=10, choices=HANDLING_CHOICES, default='ai')

    def __str__(self):
        return f"{self.platform_type} chat with {self.user_identifier or 'anonymous'}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_from_user = models.BooleanField(default=True)  # True if from user, False if from agent
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{'User' if self.is_from_user else 'Agent'} message in {self.session}"
