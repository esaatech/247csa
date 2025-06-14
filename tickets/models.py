from django.db import models
from django.contrib.auth import get_user_model
from team.models import Team, TeamMember
from team.TeamObjectBase import TeamObjectBase
import uuid

User = get_user_model()

class TicketCategory(models.Model):
    """Categories for organizing tickets (e.g., Billing, Technical Support)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teams = models.ManyToManyField(Team, related_name='ticket_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Ticket categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Ticket(TeamObjectBase):
    """Main ticket model for tracking support requests"""
    
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        ON_HOLD = 'on_hold', 'On Hold'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='ticket_images/%Y/%m/', blank=True, null=True,
                            help_text="Upload an image to help describe the issue")
    
    # Status and Priority
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    # Relationships
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.status}"

    def can_comment(self, user):
        """Check if a user can comment on this ticket"""
        # Any team member can comment
        return self.can_view(user)
    
    def can_change_status(self, user):
        """Check if a user can change the ticket status"""
        # Assigned user or team admins/owners can change status
        return (
            user == self.assigned_to or 
            self.can_edit(user)
        )

class TicketComment(models.Model):
    """Comments and updates on tickets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='ticket_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.ticket.title} by {self.author.email}"

class TicketAttachment(models.Model):
    """File attachments for tickets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='ticket_attachments'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename
