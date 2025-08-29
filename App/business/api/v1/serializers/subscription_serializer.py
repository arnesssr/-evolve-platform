from rest_framework import serializers
from ....models.subscription import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    usage_percentage = serializers.SerializerMethodField()
    days_to_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'software_type', 'plan_type', 'status', 
            'monthly_cost', 'active_users', 'max_users', 
            'usage_percentage', 'days_to_expiry'
        ]
    
    def get_usage_percentage(self, obj):
        return obj.get_usage_percentage()
    
    def get_days_to_expiry(self, obj):
        return obj.days_until_expiry()