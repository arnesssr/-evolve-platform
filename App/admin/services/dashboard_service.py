"""
Admin Dashboard Service
Business logic layer for dashboard data orchestration
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache

from ..repositories.dashboard_repository import DashboardRepository
from .audit_service import AuditService


class DashboardService:
    """
    Service for dashboard business logic
    Orchestrates data from multiple repositories and applies business rules
    """
    
    def __init__(self):
        self.repository = DashboardRepository()
        self.audit_service = AuditService()
    
    def get_dashboard_metrics(self, period='last_7_days', date_from=None, date_to=None):
        """
        Get comprehensive dashboard metrics
        Combines user, business, financial, and system metrics
        """
        cache_key = f"dashboard_metrics_{period}_{date_from}_{date_to}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Calculate date range
        start_date, end_date = self._calculate_date_range(period, date_from, date_to)
        
        # Gather metrics from all sources
        metrics = {
            'users': self.repository.get_user_metrics(start_date, end_date),
            'businesses': self.repository.get_business_metrics(start_date, end_date),
            'financial': self.repository.get_financial_metrics(start_date, end_date),
            'system': self.repository.get_system_metrics(),
            'period': period,
            'date_range': {
                'start': start_date,
                'end': end_date,
            }
        }
        
        # Add calculated metrics
        metrics['growth_rates'] = self._calculate_growth_rates(metrics)
        metrics['health_score'] = self._calculate_health_score(metrics)
        
        # Cache for 5 minutes
        cache.set(cache_key, metrics, 300)
        
        return metrics
    
    def get_recent_activities(self, limit=10):
        """Get recent admin activities with formatting"""
        activities = self.repository.get_recent_activities(limit)
        
        # Format activities for display
        formatted_activities = []
        for activity in activities:
            formatted_activities.append({
                'id': activity.id,
                'admin_user': activity.actor.get_full_name() or activity.actor.username if activity.actor else 'System',
                'action': activity.get_action_display() if hasattr(activity, 'get_action_display') else activity.action,
                'target': activity.target_type,
                'target_id': activity.target_id,
                'timestamp': activity.created_at,
                'ip_address': activity.ip_address,
                'description': activity.target_display,
            })
        
        return formatted_activities
    
    def get_system_status(self):
        """Get system status with health indicators"""
        status = self.repository.get_system_status()
        
        # Add overall health indicator
        health_indicators = [
            status['database'] == 'healthy',
            status['cache'] == 'healthy',
            status['storage'] == 'healthy',
            status['external_apis'] == 'healthy',
        ]
        
        status['overall_health'] = 'healthy' if all(health_indicators) else 'warning'
        status['healthy_services'] = sum(health_indicators)
        status['total_services'] = len(health_indicators)
        
        return status
    
    def get_quick_stats(self):
        """Get quick statistics for dashboard widgets"""
        cache_key = "dashboard_quick_stats"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        # Today's stats
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        stats = {
            'today': {
                'new_users': self.repository.get_user_metrics(today)['new_users'],
                'new_businesses': self.repository.get_business_metrics(today)['new_businesses'],
            },
            'yesterday': {
                'new_users': self.repository.get_user_metrics(yesterday, yesterday)['new_users'],
                'new_businesses': self.repository.get_business_metrics(yesterday, yesterday)['new_businesses'],
            },
        }
        
        # Calculate percentage changes
        stats['changes'] = {
            'users': self._calculate_percentage_change(
                stats['yesterday']['new_users'],
                stats['today']['new_users']
            ),
            'businesses': self._calculate_percentage_change(
                stats['yesterday']['new_businesses'],
                stats['today']['new_businesses']
            ),
        }
        
        # Cache for 1 hour
        cache.set(cache_key, stats, 3600)
        
        return stats
    
    def get_growth_trends(self, days=30):
        """Get growth trends with analysis"""
        trends = self.repository.get_growth_trends(days)
        
        # Add trend analysis
        if trends['user_growth']:
            user_counts = [item['count'] for item in trends['user_growth']]
            trends['user_trend'] = self._analyze_trend(user_counts)
        
        return trends
    
    def get_last_update_time(self):
        """Get the last update timestamp"""
        return timezone.now()
    
    def _calculate_date_range(self, period, date_from=None, date_to=None):
        """Calculate start and end dates based on period"""
        end_date = timezone.now()
        
        if period == 'custom' and date_from and date_to:
            return date_from, date_to
        elif period == 'today':
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'yesterday':
            yesterday = timezone.now() - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == 'last_7_days':
            start_date = end_date - timedelta(days=7)
        elif period == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif period == 'last_90_days':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)
        
        return start_date, end_date
    
    def _calculate_growth_rates(self, metrics):
        """Calculate growth rates from metrics"""
        # This would implement actual growth rate calculations
        # Placeholder implementation
        return {
            'users': {
                'daily': 0.05,
                'weekly': 0.15,
                'monthly': 0.25,
            },
            'businesses': {
                'daily': 0.02,
                'weekly': 0.08,
                'monthly': 0.12,
            },
            'revenue': {
                'daily': 0.03,
                'weekly': 0.10,
                'monthly': 0.20,
            },
        }
    
    def _calculate_health_score(self, metrics):
        """Calculate overall system health score"""
        # Prefer system status indicators; fall back gracefully if absent
        try:
            status = self.get_system_status()
        except Exception:
            status = {}
        
        # Evaluate health across known subsystems when available
        subsystems = ('database', 'cache', 'storage', 'external_apis')
        health_factors = []
        for key in subsystems:
            value = status.get(key)
            if value is None:
                continue
            health_factors.append(value == 'healthy')
        
        return (sum(health_factors) / len(health_factors)) * 100 if health_factors else 0
    
    def _calculate_percentage_change(self, old_value, new_value):
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        
        return ((new_value - old_value) / old_value) * 100
    
    def _analyze_trend(self, values):
        """Analyze trend direction from a list of values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend analysis - compare first and last values
        if values[-1] > values[0]:
            return 'increasing'
        elif values[-1] < values[0]:
            return 'decreasing'
        else:
            return 'stable'
