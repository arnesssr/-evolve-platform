"""Payout repository."""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Payout
from .base import BaseRepository


class PayoutRepository(BaseRepository):
    """Repository for Payout model."""
    model = Payout
    
    def get_pending_payouts(self, reseller=None):
        """Get all pending payouts."""
        queryset = self.filter(status__in=['requested', 'processing'])
        if reseller:
            queryset = queryset.filter(reseller=reseller)
        return queryset.order_by('request_date')
    
    def get_completed_payouts(self, reseller=None):
        """Get all completed payouts."""
        queryset = self.filter(status='completed')
        if reseller:
            queryset = queryset.filter(reseller=reseller)
        return queryset.order_by('-completion_date')
    
    def get_payouts_by_period(self, reseller, start_date, end_date):
        """Get payouts for a specific period."""
        return self.filter(
            reseller=reseller,
            request_date__date__gte=start_date,
            request_date__date__lte=end_date
        ).order_by('-request_date')
    
    def calculate_total_paid(self, reseller):
        """Calculate total amount paid out."""
        result = self.filter(
            reseller=reseller,
            status='completed'
        ).aggregate(total=Sum('amount'))
        return result['total'] or 0
    
    def calculate_pending_amount(self, reseller):
        """Calculate total pending payout amount."""
        result = self.filter(
            reseller=reseller,
            status__in=['requested', 'processing']
        ).aggregate(total=Sum('amount'))
        return result['total'] or 0
    
    def get_payout_summary_by_status(self, reseller):
        """Get payout summary grouped by status."""
        return self.filter(reseller=reseller).values('status').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('status')
    
    def get_payout_summary_by_method(self, reseller):
        """Get payout summary grouped by payment method."""
        return self.filter(reseller=reseller).values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('payment_method')
    
    def get_recent_payouts(self, reseller, limit=10):
        """Get recent payouts."""
        return self.filter(reseller=reseller).order_by('-request_date')[:limit]
    
    def get_payout_requests_for_processing(self):
        """Get all payout requests ready for processing."""
        return self.filter(status='requested').select_related(
            'reseller', 'reseller__user'
        ).order_by('request_date')
    
    def get_processing_payouts(self):
        """Get all payouts currently being processed."""
        return self.filter(status='processing').select_related(
            'reseller', 'reseller__user'
        ).order_by('process_date')
    
    def search_payouts(self, reseller, search_term):
        """Search payouts by reference or transaction reference."""
        return self.filter(reseller=reseller).filter(
            Q(reference_number__icontains=search_term) |
            Q(transaction_reference__icontains=search_term)
        ).order_by('-request_date')
    
    def get_monthly_payout_stats(self, reseller, months=12):
        """Get monthly payout statistics."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months)
        
        payouts = self.filter(
            reseller=reseller,
            status='completed',
            completion_date__gte=start_date
        )
        
        # Group by month
        stats = {}
        for payout in payouts:
            month_key = payout.completion_date.strftime('%Y-%m')
            if month_key not in stats:
                stats[month_key] = {
                    'amount': 0,
                    'count': 0
                }
            stats[month_key]['amount'] += payout.amount
            stats[month_key]['count'] += 1
        
        return stats
    
    def has_pending_payouts(self, reseller):
        """Check if reseller has pending payouts."""
        return self.exists(
            reseller=reseller,
            status__in=['requested', 'processing']
        )
    
    def get_reseller_payouts(self, reseller, filters=None):
        """Get payouts for a reseller with optional filters."""
        queryset = self.filter(reseller=reseller)
        
        if filters:
            # Apply status filter
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            
            # Apply date range filters
            if filters.get('start_date'):
                queryset = queryset.filter(request_date__gte=filters['start_date'])
            
            if filters.get('end_date'):
                queryset = queryset.filter(request_date__lte=filters['end_date'])
        
        return queryset.order_by('-request_date')
