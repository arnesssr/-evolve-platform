"""Serializers for reseller profile API."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from ....earnings.models.reseller import Reseller

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user basic information."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username', 'email']
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return obj.get_full_name()


class ResellerSerializer(serializers.ModelSerializer):
    """Serializer for reseller profile."""
    
    user = UserSerializer(read_only=True)
    available_balance = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True,
        source='get_available_balance'
    )
    tier_commission_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True,
        source='get_tier_commission_rate'
    )
    
    class Meta:
        model = Reseller
        fields = [
            'id', 'user', 'company_name', 'company_website', 'company_description',
            'phone_number', 'alternate_email', 'address', 'city', 'state',
            'country', 'postal_code', 'referral_code', 'tier', 'commission_rate',
            'tier_commission_rate', 'payment_method', 'is_active', 'is_verified',
            'verified_at', 'total_sales', 'total_commission_earned',
            'total_commission_paid', 'pending_commission', 'available_balance',
            'joined_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'referral_code', 'tier', 'commission_rate',
            'tier_commission_rate', 'is_verified', 'verified_at',
            'total_sales', 'total_commission_earned', 'total_commission_paid',
            'pending_commission', 'available_balance', 'joined_at',
            'created_at', 'updated_at'
        ]


class ResellerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reseller profile."""
    
    class Meta:
        model = Reseller
        fields = [
            'company_name', 'company_website', 'company_description',
            'phone_number', 'alternate_email', 'address', 'city',
            'state', 'country', 'postal_code'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        import re
        if value:
            cleaned_number = re.sub(r'\D', '', value)
            if len(cleaned_number) < 10 or len(cleaned_number) > 15:
                raise serializers.ValidationError(
                    'Please enter a valid phone number with 10-15 digits.'
                )
        return value


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment method information."""
    
    class Meta:
        model = Reseller
        fields = [
            'payment_method', 'bank_account_name', 'bank_account_number',
            'bank_name', 'bank_routing_number', 'paypal_email'
        ]
    
    def validate(self, data):
        """Validate payment method specific fields."""
        payment_method = data.get('payment_method')
        
        if payment_method == 'bank_transfer':
            required_fields = ['bank_account_name', 'bank_account_number', 'bank_name']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f'{field.replace("_", " ").title()} is required for bank transfer.'
                    })
        
        elif payment_method == 'paypal':
            if not data.get('paypal_email'):
                raise serializers.ValidationError({
                    'paypal_email': 'PayPal email is required for PayPal payments.'
                })
        
        return data


class ResellerStatsSerializer(serializers.Serializer):
    """Serializer for reseller statistics."""
    
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_commission_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_commission_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    available_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    tier = serializers.CharField()
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    is_verified = serializers.BooleanField()
    profile_completion = serializers.DictField()


class ProfileCompletionSerializer(serializers.Serializer):
    """Serializer for profile completion status."""
    
    completion_percentage = serializers.IntegerField()
    is_complete = serializers.BooleanField()
    missing_required = serializers.ListField(child=serializers.CharField())
    missing_optional = serializers.ListField(child=serializers.CharField())
    total_fields = serializers.IntegerField()
    completed_fields = serializers.IntegerField()


class ResellerListSerializer(serializers.ModelSerializer):
    """Serializer for reseller list view."""
    
    user_full_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Reseller
        fields = [
            'id', 'user_full_name', 'user_email', 'company_name',
            'referral_code', 'tier', 'commission_rate', 'is_active',
            'is_verified', 'total_sales', 'total_commission_earned',
            'joined_at'
        ]
    
    def get_user_full_name(self, obj):
        """Get user's full name."""
        return obj.user.get_full_name() or obj.user.username


class ResellerCreateSerializer(serializers.Serializer):
    """Serializer for creating a reseller profile."""
    
    company_name = serializers.CharField(required=True, max_length=255)
    phone_number = serializers.CharField(required=True, max_length=20)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True, max_length=100)
    state = serializers.CharField(required=True, max_length=100)
    country = serializers.CharField(required=True, max_length=100)
    postal_code = serializers.CharField(required=False, max_length=20, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=['bank_transfer', 'paypal', 'stripe'],
        required=True
    )
    
    # Optional fields
    company_website = serializers.URLField(required=False, allow_blank=True)
    company_description = serializers.CharField(required=False, allow_blank=True)
    alternate_email = serializers.EmailField(required=False, allow_blank=True)
    
    # Payment method specific fields
    bank_account_name = serializers.CharField(required=False, allow_blank=True)
    bank_account_number = serializers.CharField(required=False, allow_blank=True)
    bank_name = serializers.CharField(required=False, allow_blank=True)
    bank_routing_number = serializers.CharField(required=False, allow_blank=True)
    paypal_email = serializers.EmailField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate payment method specific fields."""
        payment_method = data.get('payment_method')
        
        if payment_method == 'bank_transfer':
            required_fields = ['bank_account_name', 'bank_account_number', 'bank_name']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f'{field.replace("_", " ").title()} is required for bank transfer.'
                    })
        
        elif payment_method == 'paypal':
            if not data.get('paypal_email'):
                raise serializers.ValidationError({
                    'paypal_email': 'PayPal email is required for PayPal payments.'
                })
        
        return data
