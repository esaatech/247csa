from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class FAQ(models.Model):
    RESPONSE_TYPES = [
        ('answer', 'Direct Answer'),
        ('subquestions', 'Sub-questions')
    ]

    # Content type fields for flexible relationships
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # Changed to CharField to handle UUIDs
    content_object = GenericForeignKey('content_type', 'object_id')

    question = models.TextField()
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPES, default='answer')
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['-created_at']
        # Add index for better query performance
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.question[:50]}..."

class FAQSubQuestion(models.Model):
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='sub_questions')
    question = models.TextField()
    answer = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('FAQ Sub-question')
        verbose_name_plural = _('FAQ Sub-questions')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.question[:50]}..."
