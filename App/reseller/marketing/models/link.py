"""MarketingLink model."""
from django.db import models
from App.reseller.earnings.models.reseller import Reseller
from .base import TimeStampedModel


class MarketingLink(TimeStampedModel):
    reseller = models.ForeignKey(Reseller, related_name="marketing_links", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=64, db_index=True)
    destination_url = models.URLField()
    clicks = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["reseller", "code"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.code})"

