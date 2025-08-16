"""API URL patterns for reseller module."""
from django.urls import path
from . import views

app_name = 'reseller_api'

urlpatterns = [
    # Payout endpoints
    path('payouts/request/', views.request_payout, name='request_payout'),
    
    # Invoice endpoints
    path('invoices/request/', views.request_invoice, name='request_invoice'),
]
