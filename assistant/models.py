from django.db import models

# Create your models here.
class OAuthToken(models.Model):
    user_profile = models.ForeignKey(
        'UserProfile.UserProfile',
        on_delete=models.CASCADE,
        related_name='oauth_tokens'
    )
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_type = models.CharField(max_length=50, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    scopes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class AbstractBaseMessage(models.Model):
    user_profile = models.ForeignKey('UserProfile.UserProfile', on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    recipients = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    received_at = models.DateTimeField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Email(AbstractBaseMessage):
    email_id = models.CharField(max_length=255)
    thread_id = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    labels = models.TextField(blank=True, null=True)
    attachment_count = models.IntegerField(default=0)

class WhatsAppMessage(AbstractBaseMessage):
    message_id = models.CharField(max_length=255)
    media_url = models.URLField(blank=True, null=True)
    media_type = models.CharField(max_length=50, blank=True, null=True)

