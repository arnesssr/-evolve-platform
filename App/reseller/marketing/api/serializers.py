"""Marketing API serializers (layered)."""
from rest_framework import serializers

from App.reseller.marketing.models import MarketingLink, MarketingTool, MarketingResource
from App.reseller.earnings.models import Commission
from django.db.models import Sum


class MarketingLinkSerializer(serializers.ModelSerializer):
    conversions = serializers.SerializerMethodField()
    earnings = serializers.SerializerMethodField()

    class Meta:
        model = MarketingLink
        fields = [
            "id", "title", "code", "destination_url", "clicks", "conversions", "earnings", "is_active",
            "created_at", "modified_at",
        ]
        read_only_fields = ["id", "clicks", "conversions", "earnings", "created_at", "modified_at"]

    def get_conversions(self, obj):
        # Count commissions attributed to this link code for the same reseller
        return Commission.objects.filter(
            reseller=obj.reseller,
            notes__icontains=f"link_code={obj.code}"
        ).count()

    def get_earnings(self, obj):
        # Sum commission amounts attributed to this link code
        agg = Commission.objects.filter(
            reseller=obj.reseller,
            notes__icontains=f"link_code={obj.code}"
        ).aggregate(total=Sum('amount'))
        total = agg.get('total') or 0
        # Return as string to preserve decimal precision in JSON
        return str(total)


class MarketingToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingTool
        fields = ["id", "name", "description", "docs_url", "is_active"]


class MarketingResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingResource
        fields = ["id", "title", "description", "url", "category"]

