from django.urls import path
from .views.resellers import ResellersListAPI, ResellerDetailAPI, ResellerStatsAPI

app_name = 'platform_admin_api_v1'

urlpatterns = [
    path('resellers/', ResellersListAPI.as_view(), name='resellers-list'),
    path('resellers/<int:reseller_id>/', ResellerDetailAPI.as_view(), name='resellers-detail'),
    path('resellers/<int:reseller_id>/stats/', ResellerStatsAPI.as_view(), name='resellers-stats'),
]

