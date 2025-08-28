from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator


class PlatformSettings(models.Model):
    """Singleton settings model storing platform configuration by section.
    We keep separate JSON fields for sections to allow partial updates per section.
    """
    general = models.JSONField(default=dict, blank=True)
    security = models.JSONField(default=dict, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    integrations = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'platform_admin'
        verbose_name = 'Platform Settings'
        verbose_name_plural = 'Platform Settings'

    def __str__(self):
        return f"PlatformSettings({self.pk})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
