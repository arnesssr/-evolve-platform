from rest_framework import serializers
from ....models.analytics import UsageMetric, AnalyticsReport

class UsageMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageMetric
        fields = ['metric_type', 'value', 'timestamp', 'metadata']

class AnalyticsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsReport
        fields = ['report_type', 'start_date', 'end_date', 
                 'metrics', 'generated_at']