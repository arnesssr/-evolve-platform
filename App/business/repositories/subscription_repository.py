from django.db.models import Sum
from ..models.subscription import Subscription
from django.utils import timezone

class SubscriptionRepository:
    @staticmethod
    def get_active_subscriptions(business):
        return Subscription.objects.filter(
            business=business,
            status='ACTIVE'
        )
    
    @staticmethod
    def get_total_monthly_cost(business):
        result = Subscription.objects.filter(
            business=business,
            status='ACTIVE'
        ).aggregate(total=Sum('monthly_cost'))
        return result['total'] or 0
    
    @staticmethod
    def get_subscription_analytics(subscription, months=6):
        return {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'usage_data': {
                'ERP': [65, 70, 80, 85, 90, 85],
                'SACCO': [45, 50, 55, 60, 65, 60],
                'PAYROLL': [25, 30, 35, 40, 45, 40]
            }
        }