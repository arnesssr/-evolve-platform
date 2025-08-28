"""DRF serializers for Sales submodule."""
from rest_framework import serializers

from App.reseller.sales.models import Lead, Referral


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "id", "name", "email", "phone", "company", "source", "status", "notes",
            "created_at", "modified_at",
        ]
        read_only_fields = ["id", "created_at", "modified_at"]


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = [
            "id", "referred_name", "referred_email", "referred_phone", "referral_code_used", "status", "notes",
            "created_at", "modified_at",
        ]
        read_only_fields = ["id", "created_at", "modified_at"]


class ReportsSummarySerializer(serializers.Serializer):
    leads_by_status = serializers.DictField(child=serializers.IntegerField())
    referrals_by_status = serializers.DictField(child=serializers.IntegerField())
    total_commissions = serializers.DecimalField(max_digits=12, decimal_places=2)

