from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid
from django.urls import reverse
from django.conf import settings

User = get_user_model()

class Team(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = 'public', _('Public')
        PRIVATE = 'private', _('Private')

    class DefaultRole(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        MEMBER = 'member', _('Member')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text=_("A brief description of your team's purpose"))
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_teams')
    visibility = models.CharField(
        max_length=20, 
        choices=Visibility.choices, 
        default=Visibility.PRIVATE,
        help_text=_("Public teams can be discovered by other users")
    )
    default_role = models.CharField(
        max_length=20,
        choices=DefaultRole.choices,
        default=DefaultRole.MEMBER,
        help_text=_("Default role for new team members")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class TeamMember(models.Model):
    class Roles(models.TextChoices):
        OWNER = 'owner', _('Owner')
        ADMIN = 'admin', _('Admin')
        MEMBER = 'member', _('Member')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='team_invites_sent')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['team', 'user']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.team.name} ({self.role})"
    
    @property
    def is_owner(self):
        return self.role == self.Roles.OWNER
    
    @property
    def is_admin(self):
        return self.role in [self.Roles.OWNER, self.Roles.ADMIN]

class TeamInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=TeamMember.Roles.choices, default=TeamMember.Roles.MEMBER)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_sent')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation for {self.email} to {self.team.name}"
        
    def get_accept_url(self):
        """Get the full URL for accepting the invitation"""
        accept_path = reverse('team:invited_register', kwargs={'invitation_id': self.id})
        return f"{settings.DOMAIN_NAME}{accept_path}"
        
    def get_decline_url(self):
        """Get the full URL for declining the invitation"""
        decline_path = reverse('team:decline_invitation', kwargs={'invitation_id': self.id})
        return f"{settings.DOMAIN_NAME}{decline_path}"
