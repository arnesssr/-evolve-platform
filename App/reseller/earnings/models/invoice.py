"""Invoice model."""
from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid
from .base import TimeStampedModel, InvoiceStatusChoices
from .reseller import Reseller


class Invoice(TimeStampedModel):
    """Invoice model for reseller commissions."""
    reseller = models.ForeignKey(
        Reseller,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField(blank=True)
    
    # Financial details
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatusChoices.choices,
        default=InvoiceStatusChoices.DRAFT
    )
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    
    # File storage
    pdf_file = models.FileField(
        upload_to='invoices/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Additional metadata
    line_items = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-issue_date', '-invoice_number']
        indexes = [
            models.Index(fields=['reseller', 'status']),
            models.Index(fields=['issue_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.reseller}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate a unique invoice number."""
        year = timezone.now().year
        month = timezone.now().month
        # Get the count of invoices for this month
        count = Invoice.objects.filter(
            issue_date__year=year,
            issue_date__month=month
        ).count() + 1
        return f"INV-{year}{month:02d}-{count:04d}"
    
    @property
    def is_overdue(self):
        """Check if the invoice is overdue."""
        if self.status == InvoiceStatusChoices.PAID:
            return False
        return timezone.now().date() > self.due_date
    
    @property
    def items_count(self):
        """Get the count of line items."""
        if isinstance(self.line_items, list):
            return len(self.line_items)
        return 0
    
    def calculate_total(self):
        """Calculate total from commissions."""
        from .commission import Commission
        commissions = Commission.objects.filter(invoice=self)
        self.subtotal = sum(c.amount for c in commissions)
        self.total_amount = self.subtotal + self.tax_amount
        self.save(update_fields=['subtotal', 'total_amount'])
    
    def mark_as_paid(self, payment_date=None):
        """Mark invoice as paid."""
        self.status = InvoiceStatusChoices.PAID
        self.payment_date = payment_date or timezone.now().date()
        self.save(update_fields=['status', 'payment_date'])
    
    def get_status_color(self):
        """Get bootstrap color class for status."""
        color_map = {
            InvoiceStatusChoices.DRAFT: 'secondary',
            InvoiceStatusChoices.SENT: 'info',
            InvoiceStatusChoices.PAID: 'success',
            InvoiceStatusChoices.OVERDUE: 'danger',
            InvoiceStatusChoices.CANCELLED: 'dark',
        }
        return color_map.get(self.status, 'secondary')
