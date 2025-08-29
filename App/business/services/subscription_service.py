from ..repositories.subscription_repository import SubscriptionRepository

class SubscriptionService:
    def __init__(self):
        self.repository = SubscriptionRepository()
    
    def get_subscription_dashboard_data(self, business):
        subscriptions = self.repository.get_active_subscriptions(business)
        total_cost = self.repository.get_total_monthly_cost(business)
        analytics = self.repository.get_subscription_analytics(None)  # General analytics
        
        subscription_data = []
        for sub in subscriptions:
            subscription_data.append({
                'subscription': sub,
                'usage_percentage': sub.get_usage_percentage(),
                'days_to_expiry': sub.days_until_expiry(),
            })
        
        return {
            'subscriptions': subscription_data,
            'total_monthly_cost': total_cost,
            'analytics': analytics
        }

    def upgrade_subscription(self, subscription_id, new_plan):
        # Implement upgrade logic
        pass