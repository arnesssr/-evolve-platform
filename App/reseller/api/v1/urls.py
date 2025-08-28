"""URL patterns for API v1."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.reseller_views import ResellerViewSet

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'resellers', ResellerViewSet, basename='reseller')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    # Include Sales API under the same prefix for consistency
    path('', include('App.reseller.sales.api.urls')),
    # Include Marketing API (layered)
    path('', include('App.reseller.marketing.api.urls')),
    # Include Reseller Settings API (layered)
    path('', include('App.reseller.settings.api.urls')),
]
