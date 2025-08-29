from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers.subscription_serializer import SubscriptionSerializer
from ....services.subscription_service import SubscriptionService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_data(request):
    service = SubscriptionService()
    dashboard_data = service.get_subscription_dashboard_data(request.user)
    
    return Response({
        'subscriptions': SubscriptionSerializer(
            dashboard_data['subscriptions'], 
            many=True
        ).data,
        'total_monthly_cost': dashboard_data['total_monthly_cost'],
        'analytics': dashboard_data['analytics']
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_subscription(request, subscription_id):
    service = SubscriptionService()
    result = service.upgrade_subscription(subscription_id, request.data.get('plan'))
    return Response({'status': 'success'})