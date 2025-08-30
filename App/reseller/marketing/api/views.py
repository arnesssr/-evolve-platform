"""Marketing API views (layered)."""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from App.reseller.marketing.services import (
    MarketingLinkService, MarketingToolService, MarketingResourceService
)
from .serializers import (
    MarketingLinkSerializer, MarketingToolSerializer, MarketingResourceSerializer
)


class MarketingLinkViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MarketingLinkSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'reseller_profile'):
            return []
        return MarketingLinkService().list_links(user.reseller_profile)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'reseller_profile'):
            # Auto-create reseller profile if missing
            from App.reseller.earnings.models import Reseller
            from App.models import UserProfile
            from django.db import transaction
            
            with transaction.atomic():
                # Ensure user has UserProfile with reseller role
                user_profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone': '',
                        'role': 'reseller'
                    }
                )
                
                # Update role if profile existed but wasn't reseller
                if not created and user_profile.role != 'reseller':
                    user_profile.role = 'reseller'
                    user_profile.save()
                
                # Create reseller profile
                referral_code = Reseller.generate_unique_referral_code(user.id)
                reseller_profile = Reseller.objects.create(
                    user=user,
                    referral_code=referral_code,
                    phone_number=user_profile.phone or '',
                    reseller_type='individual'  # Default type
                )
                user.reseller_profile = reseller_profile  # Update cached relation
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = MarketingLinkService().create_link(user.reseller_profile, serializer.validated_data)
        output = self.get_serializer(link)
        return Response(output.data, status=status.HTTP_201_CREATED)


class MarketingToolListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tools = MarketingToolService().list_tools()
        return Response(MarketingToolSerializer(tools, many=True).data)


class MarketingResourceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resources = MarketingResourceService().list_resources()
        return Response(MarketingResourceSerializer(resources, many=True).data)

