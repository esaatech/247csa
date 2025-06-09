from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

def generate_customer_number():
    """Generate a customer number in the format CST-YYYYMMDD-XXXXX"""
    today = timezone.now()
    date_part = today.strftime('%Y%m%d')
    
    # Get the last customer number for today
    last_customer = Customer.objects.filter(
        customer_number__startswith=f'CST-{date_part}'
    ).order_by('-customer_number').first()
    
    if last_customer:
        try:
            # Extract the sequence number and increment
            sequence = int(last_customer.customer_number.split('-')[-1]) + 1
        except ValueError:
            # If we can't parse the sequence, start from 1
            sequence = 1
    else:
        sequence = 1
    
    return f'CST-{date_part}-{sequence:05d}'

class Customer(models.Model):
    task_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    activity_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # For interactions/activities
    customer_number = models.CharField(max_length=25, unique=True, editable=False, null=True)  # Format: CST-YYYYMMDD-XXXXX
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers', null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    relationship_status = models.CharField(max_length=50, default='prospect')
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.customer_number:
            self.customer_number = generate_customer_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_number} - {self.name} ({self.company_name})"

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

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    medium = models.CharField(max_length=20, choices=MEDIUM_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_type_display()} with {self.customer.name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} for {self.customer.name}"
