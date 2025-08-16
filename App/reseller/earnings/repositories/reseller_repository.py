"""Reseller repository for data access operations."""
from typing import Optional, List, Dict, Any
from django.db.models import Q, QuerySet
from django.utils import timezone
from datetime import datetime

from ..models.reseller import Reseller
from .base import BaseRepository


class ResellerRepository(BaseRepository):
    """Repository for reseller data access."""
    
    model = Reseller
    
    def get_by_user_id(self, user_id: int) -> Optional[Reseller]:
        """
        Get reseller by user ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Reseller instance or None
        """
        try:
            return self.model.objects.get(user_id=user_id)
        except self.model.DoesNotExist:
            return None
    
    def get_by_referral_code(self, referral_code: str) -> Optional[Reseller]:
        """
        Get reseller by referral code.
        
        Args:
            referral_code: Referral code
            
        Returns:
            Reseller instance or None
        """
        try:
            return self.model.objects.get(referral_code=referral_code, is_active=True)
        except self.model.DoesNotExist:
            return None
    
    def get_active_resellers(self) -> QuerySet:
        """
        Get all active resellers.
        
        Returns:
            QuerySet of active resellers
        """
        return self.model.objects.filter(is_active=True)
    
    def get_verified_resellers(self) -> QuerySet:
        """
        Get all verified resellers.
        
        Returns:
            QuerySet of verified resellers
        """
        return self.model.objects.filter(is_verified=True, is_active=True)
    
    def verify_reseller(self, reseller_id: int) -> Reseller:
        """
        Verify a reseller's profile.
        
        Args:
            reseller_id: ID of the reseller
            
        Returns:
            Updated Reseller instance
        """
        reseller = self.get_by_id(reseller_id)
        reseller.is_verified = True
        reseller.verified_at = timezone.now()
        reseller.save(update_fields=['is_verified', 'verified_at'])
        return reseller
    
    def search(self, filters: Dict[str, Any]) -> List[Reseller]:
        """
        Search resellers based on filters.
        
        Args:
            filters: Dictionary of search filters
            
        Returns:
            List of Reseller instances
        """
        queryset = self.model.objects.all()
        
        # Text search
        if 'search' in filters:
            search_term = filters['search']
            queryset = queryset.filter(
                Q(user__username__icontains=search_term) |
                Q(user__email__icontains=search_term) |
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term) |
                Q(company_name__icontains=search_term) |
                Q(referral_code__icontains=search_term)
            )
        
        # Filter by tier
        if 'tier' in filters:
            queryset = queryset.filter(tier=filters['tier'])
        
        # Filter by verification status
        if 'is_verified' in filters:
            queryset = queryset.filter(is_verified=filters['is_verified'])
        
        # Filter by active status
        if 'is_active' in filters:
            queryset = queryset.filter(is_active=filters['is_active'])
        
        # Filter by date range
        if 'date_from' in filters:
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if 'date_to' in filters:
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        # Filter by commission range
        if 'min_commission' in filters:
            queryset = queryset.filter(total_commission_earned__gte=filters['min_commission'])
        
        if 'max_commission' in filters:
            queryset = queryset.filter(total_commission_earned__lte=filters['max_commission'])
        
        # Order by
        order_by = filters.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
        return list(queryset)
    
    def get_by_tier(self, tier: str) -> QuerySet:
        """
        Get resellers by tier.
        
        Args:
            tier: Tier level
            
        Returns:
            QuerySet of resellers
        """
        return self.model.objects.filter(tier=tier, is_active=True)
    
    def get_top_performers(self, limit: int = 10) -> List[Reseller]:
        """
        Get top performing resellers by total sales.
        
        Args:
            limit: Number of resellers to return
            
        Returns:
            List of top performing resellers
        """
        return list(
            self.model.objects.filter(is_active=True)
            .order_by('-total_sales')[:limit]
        )
    
    def get_recent_signups(self, days: int = 30) -> QuerySet:
        """
        Get resellers who signed up recently.
        
        Args:
            days: Number of days to look back
            
        Returns:
            QuerySet of recent signups
        """
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.model.objects.filter(
            created_at__gte=cutoff_date,
            is_active=True
        ).order_by('-created_at')
    
    def get_with_pending_commissions(self) -> QuerySet:
        """
        Get resellers with pending commissions.
        
        Returns:
            QuerySet of resellers with pending commissions
        """
        return self.model.objects.filter(
            pending_commission__gt=0,
            is_active=True
        ).order_by('-pending_commission')
    
    def update_metrics(self, reseller_id: int, metrics: Dict[str, Any]) -> Reseller:
        """
        Update reseller metrics.
        
        Args:
            reseller_id: ID of the reseller
            metrics: Dictionary of metrics to update
            
        Returns:
            Updated Reseller instance
        """
        allowed_metrics = [
            'total_sales', 'total_commission_earned',
            'total_commission_paid', 'pending_commission'
        ]
        
        update_data = {k: v for k, v in metrics.items() if k in allowed_metrics}
        
        return self.update(reseller_id, **update_data)
    
    def bulk_update_tiers(self) -> int:
        """
        Bulk update tiers for all resellers based on their sales.
        
        Returns:
            Number of resellers updated
        """
        updated_count = 0
        resellers = self.get_active_resellers()
        
        for reseller in resellers:
            old_tier = reseller.tier
            reseller.update_tier()
            if old_tier != reseller.tier:
                updated_count += 1
        
        return updated_count
    
    def get_incomplete_profiles(self) -> QuerySet:
        """
        Get resellers with incomplete profiles.
        
        Returns:
            QuerySet of resellers with incomplete profiles
        """
        return self.model.objects.filter(
            Q(company_name='') | Q(company_name__isnull=True) |
            Q(phone_number='') | Q(phone_number__isnull=True) |
            Q(address='') | Q(address__isnull=True) |
            Q(payment_method='') | Q(payment_method__isnull=True),
            is_active=True
        )
