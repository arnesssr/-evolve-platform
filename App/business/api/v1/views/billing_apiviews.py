from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers.billing_serializer import PaymentSerializer, InvoiceSerializer
from ....services.billing_service import BillingService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    service = BillingService()
    try:
        result = service.initiate_payment(
            subscription_id=request.data.get('subscription_id'),
            amount=request.data.get('amount'),
            payment_method=request.data.get('payment_method')
        )
        return Response({
            'status': 'success',
            'invoice': InvoiceSerializer(result['invoice']).data,
            'payment': PaymentSerializer(result['payment']).data
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mpesa_payment(request):
    service = BillingService()
    try:
        result = service.process_mpesa_payment(
            phone_number=request.data.get('phone_number'),
            amount=request.data.get('amount'),
            account_ref=request.data.get('account_ref')
        )
        return Response({'status': 'success', 'data': result})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)