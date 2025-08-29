from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers.subscription_user_serializer import SubscriptionUserSerializer
from ....services.subscription_user_service import SubscriptionUserService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_subscription_user(request, subscription_id):
    service = SubscriptionUserService()
    try:
        user = service.add_user_to_subscription(
            subscription_id=subscription_id,
            user_id=request.data.get('user_id'),
            role=request.data.get('role', 'USER')
        )
        return Response({
            'status': 'success',
            'user': SubscriptionUserSerializer(user).data
        })
    except ValueError as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_subscription_user(request, subscription_id, user_id):
    service = SubscriptionUserService()
    service.remove_user_from_subscription(subscription_id, user_id)
    return Response({'status': 'success'})