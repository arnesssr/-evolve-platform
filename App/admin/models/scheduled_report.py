from django.db import models
from django.conf import settings


class ScheduledReport(models.Model):
    """Persistent configuration for scheduled reports."""

    REPORT_TYPES = [
        ("revenue_summary", "Revenue Summary"),
        ("commission_report", "Commission Report"),
        ("payout_report", "Payout Report"),
        ("financial_overview", "Financial Overview"),
        ("cash_flow_statement", "Cash Flow Statement"),
    ]

    FORMAT_CHOICES = [
        ("pdf", "PDF"),
        ("excel", "Excel"),
        ("csv", "CSV"),
        ("html", "HTML"),
    ]

    report_type = models.CharField(max_length=64, choices=REPORT_TYPES)
    format = models.CharField(max_length=16, choices=FORMAT_CHOICES, default="pdf")
    schedule = models.CharField(max_length=64, help_text="Cron expression: m h dom mon dow")
    recipients = models.JSONField(default=list, help_text="List of recipient email addresses")
    parameters = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="scheduled_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Execution metadata (optional for MVP)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "admin_scheduled_reports"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.report_type} scheduled {self.schedule} (active={self.active})"

