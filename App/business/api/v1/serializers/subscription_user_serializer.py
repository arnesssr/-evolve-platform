from rest_framework import serializers
from ....models.subscription_user import SubscriptionUser

class SubscriptionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionUser
        fields = ['id', 'user', 'role', 'last_active', 'date_added', 'is_active']