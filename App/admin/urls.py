from django.urls import path
from . import views

app_name = 'platform_admin'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),

    # Users (mapped to existing templates)
    path('businesses/list/', views.businesses_list, name='businesses-list'),
    path('businesses/detail/<int:user_id>/', views.businesses_detail, name='businesses-detail'),

    path('resellers/list/', views.resellers_list, name='resellers-list'),
    path('resellers/detail/<int:user_id>/', views.resellers_detail, name='resellers-detail'),

    path('admins/list/', views.admins_list, name='admins-list'),
    path('admins/detail/<int:user_id>/', views.admins_detail, name='admins-detail'),

    # Products & Plans
    path('products/list/', views.products_list, name='products-list'),
    path('products/form/', views.products_form, name='products-form'),

    path('plans/list/', views.plans_list, name='plans-list'),
    path('plans/form/', views.plans_form, name='plans-form'),

    # Financial
    path('financial/revenue/', views.financial_revenue, name='financial-revenue'),
    path('financial/commissions/', views.financial_commissions, name='financial-commissions'),
    path('financial/payouts/', views.financial_payouts, name='financial-payouts'),
    path('financial/invoices/', views.financial_invoices, name='financial-invoices'),
    path('financial/transactions/', views.financial_transactions, name='financial-transactions'),

    # Analytics
    path('analytics/overview/', views.analytics_overview, name='analytics-overview'),

    # Reports
    path('reports/generate/', views.reports_generate, name='reports-generate'),
    path('reports/scheduled/', views.reports_scheduled, name='reports-scheduled'),

    # Settings
    path('settings/general/', views.settings_general, name='settings-general'),
    path('settings/security/', views.settings_security, name='settings-security'),
    path('settings/notifications/', views.settings_notifications, name='settings-notifications'),
    path('settings/integrations/', views.settings_integrations, name='settings-integrations'),

    # System
    path('system/status/', views.system_status, name='system-status'),
    path('system/logs/', views.system_logs, name='system-logs'),
    path('system/backup/', views.system_backup, name='system-backup'),
    path('system/maintenance/', views.system_maintenance, name='system-maintenance'),
]
