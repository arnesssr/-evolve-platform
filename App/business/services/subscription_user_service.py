from ..repositories.subscription_user_repository import SubscriptionUserRepository
from ..models.subscription import Subscription

class SubscriptionUserService:
    def __init__(self):
        self.repository = SubscriptionUserRepository()
    
    def add_user_to_subscription(self, subscription_id, user_id, role='USER'):
        subscription = Subscription.objects.get(id=subscription_id)
        current_users = self.repository.get_subscription_users(subscription_id).count()
        
        if current_users >= subscription.max_users:
            raise ValueError("Maximum user limit reached")
            
        return self.repository.add_user(subscription_id, user_id, role)
    
    def remove_user_from_subscription(self, subscription_id, user_id):
        self.repository.remove_user(subscription_id, user_id)