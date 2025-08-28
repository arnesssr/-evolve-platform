"""Settings API urls (layered)."""
from django.urls import path
from .views import ResellerPreferencesView

urlpatterns = [
    path('settings/preferences/', ResellerPreferencesView.as_view(), name='reseller-preferences'),
]

