"""Payout model."""
from django.db import models
from django.utils import timezone
from decimal import Decimal
from .base import TimeStampedModel, PayoutStatusChoices, PaymentMethodChoices
from .reseller import Reseller
from .invoice import Invoice


class Payout(TimeStampedModel):
    """Payout model for reseller withdrawals."""
    reseller = models.ForeignKey(
        Reseller,
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    
    # Related invoice (optional)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payouts'
    )
    
    # Payout details
    reference_number = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Payment details
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethodChoices.choices,
        default=PaymentMethodChoices.BANK_TRANSFER
    )
    payment_details = models.JSONField(default=dict, blank=True)
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=PayoutStatusChoices.choices,
        default=PayoutStatusChoices.REQUESTED
    )
    
    # Important dates
    request_date = models.DateTimeField(auto_now_add=True)
    process_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Transaction details
    transaction_reference = models.CharField(max_length=255, blank=True)
    transaction_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Additional fields
    failure_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payouts'
    )
    
    class Meta:
        db_table = 'payouts'
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['reseller', 'status']),
            models.Index(fields=['request_date']),
        ]
    
    def __str__(self):
        return f"Payout {self.reference_number} - {self.reseller}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        # Calculate net amount
        self.net_amount = self.amount - self.transaction_fee
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        """Generate a unique payout reference number."""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"PAY-{timestamp}-{self.reseller.id}"
    
    def get_status_color(self):
        """Get bootstrap color class for status."""
        color_map = {
            PayoutStatusChoices.REQUESTED: 'warning',
            PayoutStatusChoices.PROCESSING: 'info',
            PayoutStatusChoices.COMPLETED: 'success',
            PayoutStatusChoices.FAILED: 'danger',
            PayoutStatusChoices.CANCELLED: 'dark',
        }
        return color_map.get(self.status, 'secondary')
    
    def process_payout(self):
        """Mark payout as processing."""
        self.status = PayoutStatusChoices.PROCESSING
        self.process_date = timezone.now()
        self.save(update_fields=['status', 'process_date'])
    
    def complete_payout(self, transaction_reference=''):
        """Mark payout as completed."""
        self.status = PayoutStatusChoices.COMPLETED
        self.completion_date = timezone.now()
        self.transaction_reference = transaction_reference
        self.save(update_fields=['status', 'completion_date', 'transaction_reference'])
        
        # Update reseller metrics
        self.reseller.total_commission_paid += self.amount
        self.reseller.pending_commission -= self.amount
        self.reseller.save(update_fields=['total_commission_paid', 'pending_commission'])
        
        # Update related commissions
        if self.commissions.exists():
            self.commissions.update(
                status='paid',
                paid_date=timezone.now()
            )
    
    def fail_payout(self, reason=''):
        """Mark payout as failed."""
        self.status = PayoutStatusChoices.FAILED
        self.failure_reason = reason
        self.save(update_fields=['status', 'failure_reason'])
