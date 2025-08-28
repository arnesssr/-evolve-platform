"""Sales API views for Leads, Referrals, and Reports."""
from decimal import Decimal
from collections import Counter

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView

from django.db.models import Sum

from App.reseller.sales.models import Lead, Referral
from App.reseller.earnings.models.commission import Commission
from .serializers import LeadSerializer, ReferralSerializer, ReportsSummarySerializer


class LeadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LeadSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'reseller_profile'):
            return Lead.objects.none()
        return Lead.objects.filter(reseller=user.reseller_profile)

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'reseller_profile'):
            raise ValueError("Reseller profile not found for user")
        serializer.save(reseller=user.reseller_profile)


class ReferralViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'reseller_profile'):
            return Referral.objects.none()
        return Referral.objects.filter(reseller=user.reseller_profile)

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'reseller_profile'):
            raise ValueError("Reseller profile not found for user")
        serializer.save(reseller=user.reseller_profile)


class ReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'reseller_profile'):
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        reseller = user.reseller_profile

        # Leads/Referrals breakdown
        leads_counts = dict(Counter(Lead.objects.filter(reseller=reseller).values_list('status', flat=True)))
        referrals_counts = dict(Counter(Referral.objects.filter(reseller=reseller).values_list('status', flat=True)))

        # Total commissions (approved + pending) for summary
        total_commissions = Commission.objects.filter(reseller=reseller).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        data = {
            'leads_by_status': leads_counts,
            'referrals_by_status': referrals_counts,
            'total_commissions': total_commissions,
        }
        serializer = ReportsSummarySerializer(data)
        return Response(serializer.data)

