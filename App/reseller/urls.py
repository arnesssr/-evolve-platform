from django.urls import path, include
from .base_views import dashboard, leads, referrals, reports, earnings, commissions, invoices, payouts, links, tools, resources, settings
from .views import profile_views

app_name = 'reseller'

urlpatterns = [
    # Dashboard
    path('', dashboard, name='dashboard'),
    
    # Sales URLs
    path('leads/', leads, name='leads'),
    path('referrals/', referrals, name='referrals'),
    path('reports/', reports, name='reports'),
    
    # Earnings URLs
    path('earnings/', earnings, name='earnings'),
    path('commissions/', commissions, name='earnings_commissions'),
    path('invoices/', invoices, name='earnings_invoices'),
    path('payouts/', payouts, name='earnings_payouts'),
    
    # Profile URLs
    path('profile/', profile_views.profile_view, name='profile_view'),
    path('profile/edit/', profile_views.profile_edit, name='profile_edit'),
    path('profile/payment-method/', profile_views.payment_method_update, name='payment_method_update'),
    path('profile/setup/', profile_views.profile_setup, name='profile_setup'),
    path('profile/verify/', profile_views.profile_verification, name='profile_verification'),
    path('profile/completion-status/', profile_views.profile_completion_status, name='profile_completion_status'),
    path('profile/stats/', profile_views.profile_stats, name='profile_stats'),
    path('profile/deactivate/', profile_views.deactivate_profile, name='deactivate_profile'),
    
    # Marketing URLs
    path('links/', links, name='links'),
    path('tools/', tools, name='tools'),
    path('resources/', resources, name='resources'),
    
    # Settings
    path('settings/', settings, name='settings'),
    
    # API endpoints
    path('api/', include('App.reseller.earnings.api.urls')),
]
