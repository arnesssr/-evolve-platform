"""Commission model."""
from django.db import models
from decimal import Decimal
from .base import TimeStampedModel, CommissionStatusChoices
from .reseller import Reseller


class Commission(TimeStampedModel):
    """Commission tracking and calculation model."""
    reseller = models.ForeignKey(
        Reseller,
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    
    # Transaction details
    transaction_reference = models.CharField(max_length=100, unique=True)
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField(blank=True)
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=100, blank=True)
    
    # Financial details
    sale_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tier_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Status and dates
    status = models.CharField(
        max_length=10,
        choices=CommissionStatusChoices.choices,
        default=CommissionStatusChoices.PENDING
    )
    calculation_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commissions'
    )
    payout = models.ForeignKey(
        'Payout',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commissions'
    )
    
    class Meta:
        db_table = 'commissions'
        verbose_name = 'Commission'
        verbose_name_plural = 'Commissions'
        ordering = ['-calculation_date']

    def __str__(self):
        return f"Commission: {self.amount} for {self.reseller}"

    def calculate_commission(self, sale_amount: Decimal):
        """Calculate commission based on sale amount."""
        self.amount = (sale_amount * self.commission_rate / 100).quantize(Decimal('0.00'))
        self.save(update_fields=['amount'])
