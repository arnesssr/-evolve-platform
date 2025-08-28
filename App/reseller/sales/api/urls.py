"""Sales API routes."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet, ReferralViewSet, ReportsSummaryView

router = DefaultRouter()
router.register(r'sales/leads', LeadViewSet, basename='sales-leads')
router.register(r'sales/referrals', ReferralViewSet, basename='sales-referrals')

urlpatterns = [
    path('', include(router.urls)),
    path('sales/reports/summary/', ReportsSummaryView.as_view(), name='sales-reports-summary'),
]

