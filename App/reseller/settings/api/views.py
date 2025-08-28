"""Settings API views (layered)."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from App.reseller.settings.services import ResellerSettingsService


class ResellerPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'reseller_profile'):
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        prefs = ResellerSettingsService().get_preferences(user.reseller_profile)
        return Response({'preferences': prefs})

    def put(self, request):
        user = request.user
        if not hasattr(user, 'reseller_profile'):
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.get('preferences', {})
        obj = ResellerSettingsService().update_preferences(user.reseller_profile, data)
        return Response({'preferences': obj.preferences}, status=status.HTTP_200_OK)

