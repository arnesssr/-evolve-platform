"""Reseller settings model (layered)."""
from django.db import models
from App.reseller.earnings.models.reseller import Reseller


class ResellerSettings(models.Model):
    reseller = models.OneToOneField(Reseller, related_name="settings", on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ResellerSettings({self.reseller_id})"
