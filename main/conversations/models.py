import uuid
from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Conversation(models.Model):
    TYPE_CHOICES = [
        ('private', 'Private'),
        ('group', 'Group'),
        ('channel', 'Channel'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255, null=True, blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_conversations'
    )
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['type', 'is_public']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"{self.get_type_display()} Chat"
