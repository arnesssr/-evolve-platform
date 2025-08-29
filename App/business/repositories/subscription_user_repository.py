from ..models.subscription_user import SubscriptionUser
from django.db.models import Count

class SubscriptionUserRepository:
    @staticmethod
    def get_subscription_users(subscription_id):
        return SubscriptionUser.objects.filter(subscription_id=subscription_id, is_active=True)
    
    @staticmethod
    def add_user(subscription_id, user_id, role='USER'):
        return SubscriptionUser.objects.create(
            subscription_id=subscription_id,
            user_id=user_id,
            role=role
        )
    
    @staticmethod
    def remove_user(subscription_id, user_id):
        SubscriptionUser.objects.filter(
            subscription_id=subscription_id,
            user_id=user_id
        ).update(is_active=False)