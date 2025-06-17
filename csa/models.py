from django.db import models
from django.contrib.auth.models import User
import uuid
from team.models import Team
from team.TeamObjectBase import TeamObjectBase

class CSA(TeamObjectBase):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('ready', 'Ready')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    knowledge_text = models.TextField(blank=True, null=True)
    firebase_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    HANDLING_CHOICES = [
        ('ai', 'AI'),
        ('human', 'Human'),
    ]
    default_handling_mode = models.CharField(max_length=10, choices=HANDLING_CHOICES, default='ai')
    teams = models.ManyToManyField(Team, related_name='csas')
    

    def __str__(self):
        return self.name

    def get_platform_connections(self):
        from django.contrib.contenttypes.models import ContentType
        from platform_connections.models import PlatformConnection

        ctype = ContentType.objects.get_for_model(self.__class__)
        return PlatformConnection.objects.filter(content_type=ctype, object_id=self.id)
    
    class Meta:
        db_table = 'csa'
        ordering = ['-created_at']

class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    csa = models.ForeignKey(CSA, on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField()
    response_type = models.CharField(max_length=20, choices=[
        ('answer', 'Direct Answer'),
        ('subquestions', 'Sub-questions')
    ])
    answer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faq'

class SubQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='sub_questions')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sub_question'
