"""MarketingTool model."""
from django.db import models
from .base import TimeStampedModel


class MarketingTool(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    docs_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

