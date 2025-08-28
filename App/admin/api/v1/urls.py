from django.urls import path
from .views.resellers import ResellersListAPI, ResellerDetailAPI, ResellerStatsAPI
from .views.dashboard import (
    dashboard_metrics_api,
    recent_activities_api,
    system_status_api,
    quick_stats_api,
    growth_trends_api,
    dashboard_summary_api,
    refresh_dashboard_cache
)
from .views.commissions import AdminCommissionCreateAPI
from .views.products import AdminProductCreateAPI, AdminProductDetailAPI, AdminProductCountAPI
from .views.plans import AdminPlanCreateAPI, AdminPlanCountAPI
from .views.admins import AdminsCountAPI

# Finance API Views
from .views.finance.revenue import (
    RevenueMetricsView, RevenueSourceBreakdownView, 
    RevenueForecastView, RevenueTrendsView
)
from .views.finance.commissions import (
    CommissionsListView, CommissionsActionView, CommissionsBulkActionView,
    CommissionsCreateView, CommissionsExportView, CommissionsDetailView
)
from .views.finance.invoices import (
    InvoicesListView, InvoicesCreateView, InvoicesActionView,
    InvoiceDownloadView, InvoicesBulkActionView, InvoicesExportView, InvoicesDetailView
)
from .views.finance.payouts import (
    PayoutsListView, PayoutsActionView, PayoutsBulkActionView,
    PayoutsCreateView, PayoutsExportView, PayoutsDetailView, PayoutsBatchView
)
from .views.finance.transactions import (
    TransactionsListView, TransactionsMetricsView, TransactionsReconcileView,
    TransactionsExportView, TransactionsDetailView, TransactionsCashFlowView
)
from .views.finance.reports import (
    ReportsGenerateView, ReportsPreviewView, ReportsDownloadView, ReportsScheduleView
)
from .views.settings import (
    GeneralSettingsView,
    SecuritySettingsView,
    NotificationsSettingsView,
    IntegrationsSettingsView,
)

app_name = 'platform_admin_api_v1'

urlpatterns = [
    # Dashboard API endpoints
    path('dashboard/metrics/', dashboard_metrics_api, name='dashboard-metrics'),
    path('dashboard/activities/', recent_activities_api, name='dashboard-activities'),
    path('dashboard/system-status/', system_status_api, name='dashboard-system-status'),
    path('dashboard/quick-stats/', quick_stats_api, name='dashboard-quick-stats'),
    path('dashboard/growth-trends/', growth_trends_api, name='dashboard-growth-trends'),
    path('dashboard/summary/', dashboard_summary_api, name='dashboard-summary'),
    path('dashboard/refresh-cache/', refresh_dashboard_cache, name='dashboard-refresh-cache'),
    
    # Existing resellers endpoints
    path('resellers/', ResellersListAPI.as_view(), name='resellers-list'),
    path('resellers/<int:reseller_id>/', ResellerDetailAPI.as_view(), name='resellers-detail'),
    path('resellers/<int:reseller_id>/stats/', ResellerStatsAPI.as_view(), name='resellers-stats'),

    # Commission endpoints
    path('commissions/create/', AdminCommissionCreateAPI.as_view(), name='commissions-create'),

# Product endpoints
    path('products/create/', AdminProductCreateAPI.as_view(), name='products-create'),
    path('products/<int:product_id>/', AdminProductDetailAPI.as_view(), name='products-detail'),
    path('products/count/', AdminProductCountAPI.as_view(), name='products-count'),

# Plan endpoints
    path('plans/create/', AdminPlanCreateAPI.as_view(), name='plans-create'),
    path('plans/count/', AdminPlanCountAPI.as_view(), name='plans-count'),

    # Admins endpoints
    path('admins/count/', AdminsCountAPI.as_view(), name='admins-count'),
    
    # ===== FINANCE API ENDPOINTS =====
    
    # Revenue endpoints
    path('finance/revenue/metrics/', RevenueMetricsView.as_view(), name='finance-revenue-metrics'),
    path('finance/revenue/source-breakdown/', RevenueSourceBreakdownView.as_view(), name='finance-revenue-source-breakdown'),
    path('finance/revenue/forecast/', RevenueForecastView.as_view(), name='finance-revenue-forecast'),
    path('finance/revenue/trends/', RevenueTrendsView.as_view(), name='finance-revenue-trends'),
    
    # Commission management endpoints
    path('finance/commissions/', CommissionsListView.as_view(), name='finance-commissions-list'),
    path('finance/commissions/actions/', CommissionsActionView.as_view(), name='finance-commissions-actions'),
    path('finance/commissions/bulk/', CommissionsBulkActionView.as_view(), name='finance-commissions-bulk'),
    path('finance/commissions/create/', CommissionsCreateView.as_view(), name='finance-commissions-create'),
    path('finance/commissions/export/', CommissionsExportView.as_view(), name='finance-commissions-export'),
    path('finance/commissions/<int:commission_id>/', CommissionsDetailView.as_view(), name='finance-commissions-detail'),
    
    # Invoice management endpoints
    path('finance/invoices/', InvoicesListView.as_view(), name='finance-invoices-list'),
    path('finance/invoices/create/', InvoicesCreateView.as_view(), name='finance-invoices-create'),
    path('finance/invoices/actions/', InvoicesActionView.as_view(), name='finance-invoices-actions'),
    path('finance/invoices/bulk/', InvoicesBulkActionView.as_view(), name='finance-invoices-bulk'),
    path('finance/invoices/export/', InvoicesExportView.as_view(), name='finance-invoices-export'),
    path('finance/invoices/<int:invoice_id>/', InvoicesDetailView.as_view(), name='finance-invoices-detail'),
    path('finance/invoices/<int:invoice_id>/download/', InvoiceDownloadView.as_view(), name='finance-invoices-download'),
    
    # Payout management endpoints
    path('finance/payouts/', PayoutsListView.as_view(), name='finance-payouts-list'),
    path('finance/payouts/actions/', PayoutsActionView.as_view(), name='finance-payouts-actions'),
    path('finance/payouts/bulk/', PayoutsBulkActionView.as_view(), name='finance-payouts-bulk'),
    path('finance/payouts/create/', PayoutsCreateView.as_view(), name='finance-payouts-create'),
    path('finance/payouts/batch/', PayoutsBatchView.as_view(), name='finance-payouts-batch'),
    path('finance/payouts/export/', PayoutsExportView.as_view(), name='finance-payouts-export'),
    path('finance/payouts/<int:payout_id>/', PayoutsDetailView.as_view(), name='finance-payouts-detail'),
    
    # Transaction management endpoints
    path('finance/transactions/', TransactionsListView.as_view(), name='finance-transactions-list'),
    path('finance/transactions/metrics/', TransactionsMetricsView.as_view(), name='finance-transactions-metrics'),
    path('finance/transactions/reconcile/', TransactionsReconcileView.as_view(), name='finance-transactions-reconcile'),
    path('finance/transactions/export/', TransactionsExportView.as_view(), name='finance-transactions-export'),
    path('finance/transactions/cash-flow/', TransactionsCashFlowView.as_view(), name='finance-transactions-cash-flow'),
    path('finance/transactions/<int:transaction_id>/', TransactionsDetailView.as_view(), name='finance-transactions-detail'),
    
    # Financial reports endpoints
    path('finance/reports/generate/', ReportsGenerateView.as_view(), name='finance-reports-generate'),
    path('finance/reports/preview/', ReportsPreviewView.as_view(), name='finance-reports-preview'),
    path('finance/reports/schedule/', ReportsScheduleView.as_view(), name='finance-reports-schedule'),
    path('finance/reports/download/<str:filename>/', ReportsDownloadView.as_view(), name='finance-reports-download'),

    # Settings endpoints
    path('settings/general/', GeneralSettingsView.as_view(), name='settings-general'),
    path('settings/security/', SecuritySettingsView.as_view(), name='settings-security'),
    path('settings/notifications/', NotificationsSettingsView.as_view(), name='settings-notifications'),
    path('settings/integrations/', IntegrationsSettingsView.as_view(), name='settings-integrations'),
]

