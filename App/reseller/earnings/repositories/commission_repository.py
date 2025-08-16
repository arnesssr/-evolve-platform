"""Commission repository."""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Commission
from .base import BaseRepository


class CommissionRepository(BaseRepository):
    """Repository for Commission model."""
    model = Commission
    
    def get_pending_commissions(self, reseller=None):
        """Get all pending commissions."""
        queryset = self.filter(status='pending')
        if reseller:
            queryset = queryset.filter(reseller=reseller)
        return queryset.order_by('-calculation_date')
    
    def get_approved_commissions(self, reseller=None):
        """Get all approved commissions."""
        queryset = self.filter(status='approved')
        if reseller:
            queryset = queryset.filter(reseller=reseller)
        return queryset.order_by('-approval_date')
    
    def get_commissions_for_period(self, reseller, start_date, end_date):
        """Get commissions for a specific period."""
        return self.filter(
            reseller=reseller,
            calculation_date__date__gte=start_date,
            calculation_date__date__lte=end_date
        ).order_by('-calculation_date')
    
    def get_unpaid_commissions(self, reseller):
        """Get unpaid commissions for a reseller."""
        return self.filter(
            reseller=reseller,
            status__in=['pending', 'approved']
        ).order_by('calculation_date')
    
    def get_commissions_without_invoice(self, reseller):
        """Get approved commissions without an invoice."""
        return self.filter(
            reseller=reseller,
            status='approved',
            invoice__isnull=True
        ).order_by('calculation_date')
    
    def calculate_total_pending(self, reseller):
        """Calculate total pending commission amount."""
        result = self.filter(
            reseller=reseller,
            status='pending'
        ).aggregate(total=Sum('amount'))
        return result['total'] or 0
    
    def calculate_monthly_commission(self, reseller, year, month):
        """Calculate total commission for a specific month."""
        result = self.filter(
            reseller=reseller,
            calculation_date__year=year,
            calculation_date__month=month
        ).aggregate(
            total_amount=Sum('amount'),
            total_sales=Sum('sale_amount'),
            count=Count('id')
        )
        return result
    
    def get_commission_by_status(self, reseller):
        """Get commission breakdown by status."""
        return self.filter(reseller=reseller).values('status').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('status')
    
    def search_commissions(self, reseller, search_term):
        """Search commissions by various fields."""
        return self.filter(reseller=reseller).filter(
            Q(transaction_reference__icontains=search_term) |
            Q(client_name__icontains=search_term) |
            Q(product_name__icontains=search_term)
        ).order_by('-calculation_date')
    
    def get_recent_commissions(self, reseller, days=30):
        """Get recent commissions."""
        start_date = timezone.now() - timedelta(days=days)
        return self.filter(
            reseller=reseller,
            calculation_date__gte=start_date
        ).order_by('-calculation_date')
    
    def get_commission_trends(self, reseller, months=6):
        """Get commission trends for the last N months."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months)
        
        commissions = self.filter(
            reseller=reseller,
            calculation_date__gte=start_date
        )
        
        # Group by month
        trends = {}
        for commission in commissions:
            month_key = commission.calculation_date.strftime('%Y-%m')
            if month_key not in trends:
                trends[month_key] = {
                    'amount': 0,
                    'count': 0,
                    'sales': 0
                }
            trends[month_key]['amount'] += commission.amount
            trends[month_key]['count'] += 1
            trends[month_key]['sales'] += commission.sale_amount
        
        return trends
    
    def get_reseller_commissions(self, reseller, filters=None):
        """Get commissions for a reseller with optional filters."""
        queryset = self.filter(reseller=reseller)
        
        if filters:
            # Apply status filter
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            
            # Apply month filter
            if filters.get('month'):
                # Parse month in format YYYY-MM
                try:
                    year, month = filters['month'].split('-')
                    queryset = queryset.filter(
                        calculation_date__year=int(year),
                        calculation_date__month=int(month)
                    )
                except ValueError:
                    pass
            
            # Apply date range filters
            if filters.get('start_date'):
                queryset = queryset.filter(calculation_date__date__gte=filters['start_date'])
            
            if filters.get('end_date'):
                queryset = queryset.filter(calculation_date__date__lte=filters['end_date'])
        
        return queryset.order_by('-calculation_date')
