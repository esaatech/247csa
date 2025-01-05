from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email_domain = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Domain of the user's email (e.g., gmail.com, company.com)."
    )
    oauth_token = models.TextField(
        blank=True, 
        null=True, 
        help_text="OAuth access token."
    )
    refresh_token = models.TextField(
        blank=True, 
        null=True, 
        help_text="OAuth refresh token."
    )
    token_expires_at = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Access token expiration time."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def save(self, *args, **kwargs):
        if not self.email_domain and self.user.email:
            self.email_domain = self.user.email.split('@')[-1]
        super().save(*args, **kwargs)
