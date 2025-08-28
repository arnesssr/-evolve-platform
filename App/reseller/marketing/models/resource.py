"""MarketingResource model."""
from django.db import models
from .base import TimeStampedModel


class MarketingResource(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField()
    category = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

