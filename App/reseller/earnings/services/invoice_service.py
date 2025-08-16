"""Invoice service for handling invoice logic."""
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from ..models import Invoice, Commission, Reseller
from .base import BaseService


class InvoiceService(BaseService):
    """Service class to manage invoices."""
    
    def create_invoice(self, reseller, period_start, period_end, description=''):
        """Create an invoice for a reseller for a specific period."""
        self.validate_required_fields(
            {'reseller': reseller, 'period_start': period_start, 'period_end': period_end},
            ['reseller', 'period_start', 'period_end']
        )
        
        if period_start > period_end:
            raise ValidationError("Period start date cannot be after end date.")
        
        # Calculate due date (30 days from issue date)
        issue_date = timezone.now().date()
        due_date = issue_date + timedelta(days=30)
        
        # Create the invoice
        invoice = Invoice.objects.create(
            reseller=reseller,
            period_start=period_start,
            period_end=period_end,
            description=description or f"Commission invoice for {period_start} to {period_end}",
            issue_date=issue_date,
            due_date=due_date,
            status='draft'
        )
        
        self.log_info(f"Invoice created: {invoice.invoice_number}")
        return invoice
    
    @transaction.atomic
    def generate_invoice_from_commissions(self, reseller, commission_ids=None, period_start=None, period_end=None):
        """Generate an invoice from approved commissions."""
        # Get approved commissions
        commissions = Commission.objects.filter(
            reseller=reseller,
            status='approved',
            invoice__isnull=True
        )
        
        if commission_ids:
            commissions = commissions.filter(id__in=commission_ids)
        elif period_start and period_end:
            commissions = commissions.filter(
                calculation_date__date__gte=period_start,
                calculation_date__date__lte=period_end
            )
        
        if not commissions.exists():
            raise ValidationError("No approved commissions found for the specified criteria.")
        
        # Create invoice
        if not period_start:
            period_start = commissions.earliest('calculation_date').calculation_date.date()
        if not period_end:
            period_end = commissions.latest('calculation_date').calculation_date.date()
        
        invoice = self.create_invoice(reseller, period_start, period_end)
        
        # Link commissions to invoice and calculate total
        total_amount = Decimal('0.00')
        line_items = []
        
        for commission in commissions:
            commission.invoice = invoice
            commission.save(update_fields=['invoice'])
            total_amount += commission.amount
            
            line_items.append({
                'description': f"{commission.product_name} - {commission.client_name}",
                'amount': str(commission.amount),
                'reference': commission.transaction_reference,
                'date': commission.calculation_date.isoformat()
            })
        
        # Update invoice totals
        invoice.subtotal = total_amount
        invoice.total_amount = total_amount
        invoice.line_items = line_items
        invoice.save(update_fields=['subtotal', 'total_amount', 'line_items'])
        
        self.log_info(f"Invoice generated with {commissions.count()} commissions, total: {total_amount}")
        return invoice
    
    def send_invoice(self, invoice_id):
        """Send an invoice to the reseller."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            
            if invoice.status not in ['draft', 'sent']:
                raise ValidationError("Only draft or sent invoices can be sent.")
            
            # Here you would implement actual email sending logic
            # For now, we'll just update the status
            invoice.status = 'sent'
            invoice.save(update_fields=['status'])
            
            self.log_info(f"Invoice sent: {invoice.invoice_number}")
            return invoice
        except Invoice.DoesNotExist:
            raise ValidationError("Invoice not found.")
    
    def mark_invoice_paid(self, invoice_id, payment_date=None):
        """Mark an invoice as paid."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            
            if invoice.status == 'paid':
                raise ValidationError("Invoice is already paid.")
            
            invoice.status = 'paid'
            invoice.payment_date = payment_date or timezone.now().date()
            invoice.save(update_fields=['status', 'payment_date'])
            
            # Update related commissions
            Commission.objects.filter(invoice=invoice).update(
                status='paid',
                paid_date=timezone.now()
            )
            
            self.log_info(f"Invoice marked as paid: {invoice.invoice_number}")
            return invoice
        except Invoice.DoesNotExist:
            raise ValidationError("Invoice not found.")
    
    def cancel_invoice(self, invoice_id, reason=''):
        """Cancel an invoice."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            
            if invoice.status == 'paid':
                raise ValidationError("Cannot cancel a paid invoice.")
            
            # Unlink commissions
            Commission.objects.filter(invoice=invoice).update(invoice=None)
            
            invoice.status = 'cancelled'
            invoice.notes = f"Cancelled: {reason}" if reason else "Cancelled"
            invoice.save(update_fields=['status', 'notes'])
            
            self.log_info(f"Invoice cancelled: {invoice.invoice_number}")
            return invoice
        except Invoice.DoesNotExist:
            raise ValidationError("Invoice not found.")
    
    def get_reseller_invoices(self, reseller, filters=None):
        """Get invoices for a specific reseller with optional filters."""
        queryset = Invoice.objects.filter(reseller=reseller)
        
        if filters:
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'year' in filters:
                queryset = queryset.filter(issue_date__year=filters['year'])
            if 'search' in filters:
                queryset = queryset.filter(
                    models.Q(invoice_number__icontains=filters['search']) |
                    models.Q(description__icontains=filters['search'])
                )
        
        return queryset.order_by('-issue_date')
    
    def get_invoice_summary(self, reseller, year=None):
        """Get invoice summary for a reseller."""
        from django.db.models import Sum, Count
        
        if not year:
            year = timezone.now().year
        
        invoices = Invoice.objects.filter(
            reseller=reseller,
            issue_date__year=year
        )
        
        summary = {
            'year': year,
            'total_invoices': invoices.count(),
            'paid_invoices': invoices.filter(status='paid').count(),
            'pending_invoices': invoices.filter(status__in=['draft', 'sent']).count(),
            'total_amount': invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
            'paid_amount': invoices.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
            'pending_amount': invoices.filter(status__in=['draft', 'sent']).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
        }
        
        # Calculate year-over-year growth
        previous_year = year - 1
        previous_total = Invoice.objects.filter(
            reseller=reseller,
            issue_date__year=previous_year
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
        
        if previous_total > 0:
            summary['year_growth'] = ((summary['total_amount'] - previous_total) / previous_total * 100).quantize(Decimal('0.01'))
        else:
            summary['year_growth'] = Decimal('0.00')
        
        return summary
    
    def check_overdue_invoices(self):
        """Check and update overdue invoices."""
        today = timezone.now().date()
        overdue_invoices = Invoice.objects.filter(
            status='sent',
            due_date__lt=today
        )
        
        count = overdue_invoices.update(status='overdue')
        self.log_info(f"Updated {count} invoices to overdue status.")
        
        return count
