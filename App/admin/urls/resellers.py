from django.urls import path
from App.admin.views_resellers import (
    AdminResellerListView,
    AdminResellerDetailView,
    AdminResellerExportView,
    AdminResellerBulkActionView,
    AdminResellerCreateView,
    AdminResellerEditView,
    AdminResellerSuspendView,
    AdminResellerResumeView,
    AdminResellerPayoutView,
    AdminResellerMessageView,
    AdminResellerStatsView,
)

urlpatterns = [
    path('resellers/list/', AdminResellerListView.as_view(), name='resellers-list'),
    path('resellers/detail/<int:reseller_id>/', AdminResellerDetailView.as_view(), name='resellers-detail'),

    path('resellers/export/', AdminResellerExportView.as_view(), name='resellers-export'),
    path('resellers/bulk/', AdminResellerBulkActionView.as_view(), name='resellers-bulk'),

    path('resellers/create/', AdminResellerCreateView.as_view(), name='reseller-create'),
    path('resellers/edit/<int:reseller_id>/', AdminResellerEditView.as_view(), name='reseller-edit'),

    path('resellers/suspend/<int:reseller_id>/', AdminResellerSuspendView.as_view(), name='reseller-suspend'),
    path('resellers/resume/<int:reseller_id>/', AdminResellerResumeView.as_view(), name='reseller-resume'),

    path('resellers/payout/<int:reseller_id>/', AdminResellerPayoutView.as_view(), name='reseller-payout'),
    path('resellers/message/', AdminResellerMessageView.as_view(), name='reseller-message'),

    # Optional JSON endpoint for charts/stats
    path('resellers/stats/<int:reseller_id>/', AdminResellerStatsView.as_view(), name='reseller-stats'),
]

