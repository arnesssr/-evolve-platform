"""Invoice repository."""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Invoice
from .base import BaseRepository


class InvoiceRepository(BaseRepository):
    """Repository for Invoice model."""
    model = Invoice
    
    def get_unpaid_invoices(self, reseller=None):
        """Get all unpaid invoices."""
        queryset = self.filter(status__in=['draft', 'sent', 'overdue'])
        if reseller:
            queryset = queryset.filter(reseller=reseller)
        return queryset.order_by('due_date')
    
    def get_overdue_invoices(self, reseller=None):
        """Get overdue invoices."""
        today = timezone.now().date()
        queryset = self.filter(
            status__in=['sent', 'overdue'],
            due_date__lt=today
        )
        if reseller:
            queryset = queryset.filter(reseller=reseller)
        return queryset.order_by('due_date')
    
    def get_invoices_by_year(self, reseller, year):
        """Get invoices for a specific year."""
        return self.filter(
            reseller=reseller,
            issue_date__year=year
        ).order_by('-issue_date')
    
    def get_invoices_by_period(self, reseller, start_date, end_date):
        """Get invoices for a specific period."""
        return self.filter(
            reseller=reseller,
            issue_date__gte=start_date,
            issue_date__lte=end_date
        ).order_by('-issue_date')
    
    def calculate_total_unpaid(self, reseller):
        """Calculate total unpaid invoice amount."""
        result = self.filter(
            reseller=reseller,
            status__in=['draft', 'sent', 'overdue']
        ).aggregate(total=Sum('total_amount'))
        return result['total'] or 0
    
    def calculate_yearly_total(self, reseller, year):
        """Calculate total invoice amount for a year."""
        result = self.filter(
            reseller=reseller,
            issue_date__year=year
        ).aggregate(
            total_amount=Sum('total_amount'),
            count=Count('id')
        )
        return result
    
    def get_invoice_summary_by_status(self, reseller):
        """Get invoice summary grouped by status."""
        return self.filter(reseller=reseller).values('status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('status')
    
    def search_invoices(self, reseller, search_term):
        """Search invoices by number or description."""
        return self.filter(reseller=reseller).filter(
            Q(invoice_number__icontains=search_term) |
            Q(description__icontains=search_term)
        ).order_by('-issue_date')
    
    def get_recent_invoices(self, reseller, limit=10):
        """Get recent invoices."""
        return self.filter(reseller=reseller).order_by('-issue_date')[:limit]
    
    def get_available_years(self, reseller):
        """Get list of years that have invoices."""
        years = self.filter(reseller=reseller).dates('issue_date', 'year', order='DESC')
        return [date.year for date in years]
    
    def mark_overdue_invoices(self):
        """Mark sent invoices as overdue if past due date."""
        today = timezone.now().date()
        return self.filter(
            status='sent',
            due_date__lt=today
        ).update(status='overdue')
    
    def get_next_invoice_number(self):
        """Generate next invoice number."""
        year = timezone.now().year
        month = timezone.now().month
        
        # Get the last invoice for current month
        last_invoice = self.filter(
            issue_date__year=year,
            issue_date__month=month
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            # Extract the sequence number from the last invoice
            parts = last_invoice.invoice_number.split('-')
            if len(parts) == 3:
                sequence = int(parts[2]) + 1
            else:
                sequence = 1
        else:
            sequence = 1
        
        return f"INV-{year}{month:02d}-{sequence:04d}"
    
    def get_reseller_invoices(self, reseller, filters=None):
        """Get invoices for a reseller with optional filters."""
        queryset = self.filter(reseller=reseller)
        
        if filters:
            # Apply status filter
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            
            # Apply year filter
            if filters.get('year'):
                try:
                    year = int(filters['year'])
                    queryset = queryset.filter(issue_date__year=year)
                except ValueError:
                    pass
            
            # Apply date range filters
            if filters.get('start_date'):
                queryset = queryset.filter(issue_date__gte=filters['start_date'])
            
            if filters.get('end_date'):
                queryset = queryset.filter(issue_date__lte=filters['end_date'])
        
        return queryset.order_by('-issue_date')
