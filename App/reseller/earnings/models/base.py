"""Base models for the reseller module."""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base model with created and modified timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class StatusChoices(models.TextChoices):
    """Common status choices used across models."""
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    APPROVED = 'approved', 'Approved'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class InvoiceStatusChoices(models.TextChoices):
    """Invoice specific status choices."""
    DRAFT = 'draft', 'Draft'
    SENT = 'sent', 'Sent'
    PAID = 'paid', 'Paid'
    OVERDUE = 'overdue', 'Overdue'
    CANCELLED = 'cancelled', 'Cancelled'


class CommissionStatusChoices(models.TextChoices):
    """Commission specific status choices."""
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    PAID = 'paid', 'Paid'
    REJECTED = 'rejected', 'Rejected'


class PayoutStatusChoices(models.TextChoices):
    """Payout specific status choices."""
    REQUESTED = 'requested', 'Requested'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class PaymentMethodChoices(models.TextChoices):
    """Payment method choices for payouts."""
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    PAYPAL = 'paypal', 'PayPal'
    STRIPE = 'stripe', 'Stripe'
    CHECK = 'check', 'Check'
    OTHER = 'other', 'Other'


class TierChoices(models.TextChoices):
    """Partnership tier choices."""
    BRONZE = 'bronze', 'Bronze'
    SILVER = 'silver', 'Silver'
    GOLD = 'gold', 'Gold'
    PLATINUM = 'platinum', 'Platinum'
