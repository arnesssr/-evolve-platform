"""Sales models definitions."""
from django.db import models
from django.conf import settings

from App.reseller.earnings.models.reseller import Reseller


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LeadStatusChoices(models.TextChoices):
    NEW = "new", "New"
    CONTACTED = "contacted", "Contacted"
    QUALIFIED = "qualified", "Qualified"
    LOST = "lost", "Lost"
    CONVERTED = "converted", "Converted"


class ReferralStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    REGISTERED = "registered", "Registered"
    PURCHASED = "purchased", "Purchased"
    REJECTED = "rejected", "Rejected"


class ReportTypeChoices(models.TextChoices):
    SALES_OVERVIEW = "sales_overview", "Sales Overview"
    CONVERSIONS = "conversions", "Conversions"
    REFERRAL_PERFORMANCE = "referral_performance", "Referral Performance"


class Lead(TimeStampedModel):
    reseller = models.ForeignKey(Reseller, related_name="leads", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=LeadStatusChoices.choices, default=LeadStatusChoices.NEW)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["reseller", "status"]),
            models.Index(fields=["email"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class Referral(TimeStampedModel):
    reseller = models.ForeignKey(Reseller, related_name="referrals", on_delete=models.CASCADE)
    referred_name = models.CharField(max_length=255)
    referred_email = models.EmailField()
    referred_phone = models.CharField(max_length=50, blank=True)
    referral_code_used = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=ReferralStatusChoices.choices, default=ReferralStatusChoices.PENDING)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["reseller", "status"]),
            models.Index(fields=["referred_email"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.referred_name} <{self.referred_email}>"


class SalesReport(TimeStampedModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sales_reports", on_delete=models.CASCADE)
    report_type = models.CharField(max_length=32, choices=ReportTypeChoices.choices, default=ReportTypeChoices.SALES_OVERVIEW)
    name = models.CharField(max_length=255, blank=True)
    filters_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name or f"Report {self.id} ({self.report_type})"

