from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers.analytics_serializers import UsageMetricSerializer, AnalyticsReportSerializer
from ....services import AnalyticsService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_analytics(request, subscription_id):
    service = AnalyticsService()
    analytics = service.get_subscription_analytics(subscription_id)
    
    return Response({
        'metrics': UsageMetricSerializer(analytics['metrics'], many=True).data,
        'monthly_report': AnalyticsReportSerializer(analytics['monthly_report']).data,
        'summary': analytics['summary']
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_feature_usage(request, subscription_id):
    service = AnalyticsService()
    metric = service.track_feature_usage(
        subscription_id=subscription_id,
        feature_name=request.data.get('feature')
    )
    return Response(UsageMetricSerializer(metric).data)