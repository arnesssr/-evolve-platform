"""Marketing API urls (layered)."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MarketingLinkViewSet, MarketingToolListView, MarketingResourceListView

router = DefaultRouter()
router.register(r'marketing/links', MarketingLinkViewSet, basename='marketing-links')

urlpatterns = [
    path('', include(router.urls)),
    path('marketing/tools/', MarketingToolListView.as_view(), name='marketing-tools'),
    path('marketing/resources/', MarketingResourceListView.as_view(), name='marketing-resources'),
]

