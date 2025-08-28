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
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
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

