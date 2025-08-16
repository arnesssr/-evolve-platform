"""Views for the Reseller API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ....earnings.models.reseller import Reseller
from ....earnings.services.reseller_service import ResellerService
from ..serializers.reseller_serializers import (
    ResellerSerializer, ResellerProfileUpdateSerializer,
    PaymentMethodSerializer, ResellerStatsSerializer,
    ResellerListSerializer, ResellerCreateSerializer
)


class ResellerViewSet(viewsets.ModelViewSet):
    """API endpoint for managing reseller profiles."""
    
    queryset = Reseller.objects.all()
    serializer_class = ResellerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user and query parameters."""
        user = self.request.user
        
        # Allow access only to the user's own profile
        if not user.is_staff:
            return self.queryset.filter(user=user)
        
        # Allow staff to filter based on query parameters
        queryset = self.queryset
        filters = self.request.query_params
        
        # Apply filters here if needed
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """Get the authenticated user's profile."""
        try:
            reseller = request.user.reseller_profile
            serializer = self.get_serializer(reseller)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reseller.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request, pk=None):
        """Update profile information."""
        instance = self.get_object()
        serializer = ResellerProfileUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated])
    def update_payment_method(self, request, pk=None):
        """Update payment method information."""
        instance = self.get_object()
        serializer = PaymentMethodSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request, pk=None):
        """Get comprehensive statistics for a reseller."""
        instance = self.get_object()
        service = ResellerService()
        stats = service.get_reseller_stats(instance.id)
        serializer = ResellerStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """Handle reseller profile creation."""
        serializer = ResellerCreateSerializer(data=request.data)
        if serializer.is_valid():
            service = ResellerService()
            try:
                reseller = service.create_reseller_profile(request.user, serializer.validated_data)
                output_serializer = self.get_serializer(reseller)
                return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

