from rest_framework import serializers


class GeneralSettingsSerializer(serializers.Serializer):
    platform_name = serializers.CharField(required=False, allow_blank=True)
    platform_url = serializers.URLField(required=False, allow_blank=True)
    support_email = serializers.EmailField(required=False, allow_blank=True)
    timezone = serializers.CharField(required=False, allow_blank=True)
    default_currency = serializers.ChoiceField(required=False, choices=[
        ('USD', 'USD'), ('EUR', 'EUR'), ('KES', 'KES'), ('GBP', 'GBP')
    ])
    default_language = serializers.ChoiceField(required=False, choices=[
        ('en', 'English'), ('sw', 'Swahili')
    ])


class SecuritySettingsSerializer(serializers.Serializer):
    two_factor_enabled = serializers.BooleanField(required=False)
    password_min_length = serializers.IntegerField(required=False, min_value=6, default=8)


class NotificationsSettingsSerializer(serializers.Serializer):
    email_sender_name = serializers.CharField(required=False, allow_blank=True)
    email_sender_address = serializers.EmailField(required=False, allow_blank=True)
    enable_system_emails = serializers.BooleanField(required=False)


class IntegrationsSettingsSerializer(serializers.Serializer):
    webhook_url = serializers.URLField(required=False, allow_blank=True)
    slack_webhook_url = serializers.URLField(required=False, allow_blank=True)
    api_enabled = serializers.BooleanField(required=False)
