"""
Admin Dashboard API Serializers
Serializers for dashboard API endpoints
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics"""
    
    class UserMetricsSerializer(serializers.Serializer):
        total_users = serializers.IntegerField()
        new_users = serializers.IntegerField()
        active_users = serializers.IntegerField()
        verified_users = serializers.IntegerField()
    
    class BusinessMetricsSerializer(serializers.Serializer):
        total_businesses = serializers.IntegerField()
        new_businesses = serializers.IntegerField()
        active_businesses = serializers.IntegerField()
        verified_businesses = serializers.IntegerField()
    
    class FinancialMetricsSerializer(serializers.Serializer):
        total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
        monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
        pending_payouts = serializers.DecimalField(max_digits=12, decimal_places=2)
        completed_transactions = serializers.IntegerField()
        failed_transactions = serializers.IntegerField()
    
    class SystemMetricsSerializer(serializers.Serializer):
        database_size = serializers.IntegerField()
        active_connections = serializers.IntegerField()
    
    class DateRangeSerializer(serializers.Serializer):
        start = serializers.DateTimeField()
        end = serializers.DateTimeField()
    
    class GrowthRatesSerializer(serializers.Serializer):
        class RateSerializer(serializers.Serializer):
            daily = serializers.FloatField()
            weekly = serializers.FloatField()
            monthly = serializers.FloatField()
        
        users = RateSerializer()
        businesses = RateSerializer()
        revenue = RateSerializer()
    
    users = UserMetricsSerializer()
    businesses = BusinessMetricsSerializer()
    financial = FinancialMetricsSerializer()
    system = SystemMetricsSerializer()
    period = serializers.CharField()
    date_range = DateRangeSerializer()
    growth_rates = GrowthRatesSerializer()
    health_score = serializers.FloatField()


class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent admin activities"""
    id = serializers.IntegerField()
    admin_user = serializers.CharField()
    action = serializers.CharField()
    target = serializers.CharField()
    target_id = serializers.CharField(allow_null=True)
    timestamp = serializers.DateTimeField()
    ip_address = serializers.CharField(allow_null=True, allow_blank=True)
    description = serializers.CharField(allow_blank=True)


class SystemStatusSerializer(serializers.Serializer):
    """Serializer for system status"""
    database = serializers.ChoiceField(choices=['healthy', 'warning', 'error'])
    cache = serializers.ChoiceField(choices=['healthy', 'warning', 'error'])
    storage = serializers.ChoiceField(choices=['healthy', 'warning', 'error'])
    external_apis = serializers.ChoiceField(choices=['healthy', 'warning', 'error'])
    overall_health = serializers.ChoiceField(choices=['healthy', 'warning', 'error'])
    healthy_services = serializers.IntegerField()
    total_services = serializers.IntegerField()
    last_backup = serializers.DateTimeField()


class QuickStatsSerializer(serializers.Serializer):
    """Serializer for quick statistics"""
    
    class DayStatsSerializer(serializers.Serializer):
        new_users = serializers.IntegerField()
        new_businesses = serializers.IntegerField()
    
    class ChangesSerializer(serializers.Serializer):
        users = serializers.FloatField()
        businesses = serializers.FloatField()
    
    today = DayStatsSerializer()
    yesterday = DayStatsSerializer()
    changes = ChangesSerializer()


class GrowthTrendSerializer(serializers.Serializer):
    """Serializer for growth trends"""
    
    class GrowthDataPointSerializer(serializers.Serializer):
        date = serializers.DateField()
        count = serializers.IntegerField()
    
    user_growth = GrowthDataPointSerializer(many=True)
    business_growth = GrowthDataPointSerializer(many=True)
    revenue_growth = GrowthDataPointSerializer(many=True)
    user_trend = serializers.ChoiceField(
        choices=['increasing', 'decreasing', 'stable'], 
        required=False
    )


class DashboardFilterSerializer(serializers.Serializer):
    """Serializer for dashboard filter parameters"""
    period = serializers.ChoiceField(
        choices=['today', 'yesterday', 'last_7_days', 'last_30_days', 'last_90_days', 'custom'],
        default='last_7_days'
    )
    metric_type = serializers.ChoiceField(
        choices=['all', 'users', 'revenue', 'transactions', 'system'],
        default='all'
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    refresh_interval = serializers.IntegerField(min_value=10, max_value=300, default=30)
    
    def validate(self, data):
        """Validate filter parameters"""
        period = data.get('period')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if period == 'custom':
            if not date_from or not date_to:
                raise serializers.ValidationError(
                    "Custom date range requires both start and end dates."
                )
            
            if date_from > date_to:
                raise serializers.ValidationError(
                    "Start date must be before end date."
                )
        
        return data
