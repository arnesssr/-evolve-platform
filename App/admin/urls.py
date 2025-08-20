from django.urls import path, include
from . import views

app_name = 'admin'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Businesses (User Management)
    path('businesses/list/', views.users_list, name='businesses-list'),
    path('businesses/detail/<int:user_id>/', views.users_profile, name='businesses-detail'),
    
    # Resellers
    path('resellers/list/', views.users_list, name='resellers-list'),
    path('resellers/detail/<int:user_id>/', views.users_profile, name='resellers-detail'),
    
    # Administrators
    path('admins/list/', views.users_list, name='admins-list'),
    path('admins/detail/<int:user_id>/', views.users_profile, name='admins-detail'),
    
    # Products
    path('products/list/', views.ecommerce_products, name='products-list'),
    path('products/form/', views.ecommerce_products, name='products-form'),
    
    # Plans
    path('plans/list/', views.ecommerce_products, name='plans-list'),
    path('plans/form/', views.ecommerce_products, name='plans-form'),
    
    # Financial
    path('financial/revenue/', views.financial_overview, name='financial-revenue'),
    path('financial/commissions/', views.financial_overview, name='financial-commissions'),
    path('financial/payouts/', views.financial_payouts, name='financial-payouts'),
    path('financial/invoices/', views.financial_invoices, name='financial-invoices'),
    path('financial/transactions/', views.financial_transactions, name='financial-transactions'),
    
    # Analytics
    path('analytics/overview/', views.analytics_overview, name='analytics-overview'),
    path('analytics/users/', views.analytics_users, name='analytics-users'),
    path('analytics/content/', views.analytics_content, name='analytics-content'),
    path('analytics/sales/', views.analytics_sales, name='analytics-sales'),
    
    # Reports
    path('reports/generate/', views.reports_generate, name='reports-generate'),
    path('reports/scheduled/', views.reports_scheduled, name='reports-scheduled'),
    
    # Settings
    path('settings/general/', views.settings_general, name='settings-general'),
    path('settings/security/', views.settings_security, name='settings-security'),
    path('settings/notifications/', views.settings_notifications, name='settings-notifications'),
    path('settings/integrations/', views.settings_integrations, name='settings-integrations'),
    
    # System
    path('system/status/', views.system_logs, name='system-status'),
    path('system/logs/', views.system_logs, name='system-logs'),
    path('system/backup/', views.system_backup, name='system-backup'),
    path('system/maintenance/', views.system_maintenance, name='system-maintenance'),
]
