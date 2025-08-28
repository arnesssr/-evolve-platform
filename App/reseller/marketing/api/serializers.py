"""Marketing API serializers (layered)."""
from rest_framework import serializers

from App.reseller.marketing.models import MarketingLink, MarketingTool, MarketingResource


class MarketingLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingLink
        fields = [
            "id", "title", "code", "destination_url", "clicks", "is_active",
            "created_at", "modified_at",
        ]
        read_only_fields = ["id", "clicks", "created_at", "modified_at"]


class MarketingToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingTool
        fields = ["id", "name", "description", "docs_url", "is_active"]


class MarketingResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingResource
        fields = ["id", "title", "description", "url", "category"]

