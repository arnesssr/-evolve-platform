from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    """Admin audit log for critical actions."""
    ACTION_CHOICES = [
        ("suspend", "Suspend Reseller"),
        ("resume", "Resume Reseller"),
        ("payout", "Process Payout"),
        ("edit", "Edit Reseller"),
        ("bulk", "Bulk Action"),
        ("message", "Send Message"),
        ("export", "Export Data"),
    ]

    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="admin_actions")
    target_type = models.CharField(max_length=64, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    target_display = models.CharField(max_length=255, blank=True)

    details = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)

    class Meta:
        db_table = "admin_audit_logs"
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self):
        return f"{self.action} by {self.actor_id} on {self.target_type}:{self.target_id} at {self.created_at}"

