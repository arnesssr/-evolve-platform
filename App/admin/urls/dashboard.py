"""
Admin Dashboard URL Configuration
"""
from django.urls import path
from ..views.dashboard import dashboard_view, dashboard_metrics_ajax

app_name = 'admin_dashboard'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('metrics/', dashboard_metrics_ajax, name='dashboard_metrics_ajax'),
]
