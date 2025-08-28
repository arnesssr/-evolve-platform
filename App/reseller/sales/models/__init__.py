"""Sales models package exports."""
from .models import TimeStampedModel, LeadStatusChoices, ReferralStatusChoices, ReportTypeChoices, Lead, Referral, SalesReport

__all__ = [
    "TimeStampedModel",
    "LeadStatusChoices",
    "ReferralStatusChoices",
    "ReportTypeChoices",
    "Lead",
    "Referral",
    "SalesReport",
]

