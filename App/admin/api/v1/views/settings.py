from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from App.admin.services.settings_service import SettingsService
from App.admin.api.v1.serializers.settings import (
    GeneralSettingsSerializer,
    SecuritySettingsSerializer,
    NotificationsSettingsSerializer,
    IntegrationsSettingsSerializer,
)


class GeneralSettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = SettingsService.get_section('general')
        return Response(data)

    def put(self, request):
        serializer = GeneralSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = SettingsService.update_section('general', serializer.validated_data)
        return Response(updated)


class SecuritySettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(SettingsService.get_section('security'))

    def put(self, request):
        serializer = SecuritySettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(SettingsService.update_section('security', serializer.validated_data))


class NotificationsSettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(SettingsService.get_section('notifications'))

    def put(self, request):
        serializer = NotificationsSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(SettingsService.update_section('notifications', serializer.validated_data))


class IntegrationsSettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(SettingsService.get_section('integrations'))

    def put(self, request):
        serializer = IntegrationsSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(SettingsService.update_section('integrations', serializer.validated_data))
