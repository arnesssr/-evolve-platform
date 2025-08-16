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
]
