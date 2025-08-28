"""
Admin Dashboard Views
Handles the main admin dashboard page rendering
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..services.dashboard_service import DashboardService
from ..forms.dashboard import DashboardFilterForm


@login_required(login_url='/login/')  # Use your app's login URL
def dashboard_view(request):
    """
    Main admin dashboard view
    Shows overview metrics, recent activities, and system status
    """
    service = DashboardService()
    form = DashboardFilterForm(request.GET or None)
    
    context = {
        'form': form,
        'metrics': service.get_dashboard_metrics(),
        'recent_activities': service.get_recent_activities(limit=10),
        'system_status': service.get_system_status(),
        'quick_stats': service.get_quick_stats(),
    }
    
    return render(request, 'dashboards/admin/pages/dashboard.html', context)


@login_required(login_url='/login/')
def dashboard_metrics_ajax(request):
    """
    AJAX endpoint for real-time dashboard metrics
    """
    service = DashboardService()
    
    data = {
        'metrics': service.get_dashboard_metrics(),
        'system_status': service.get_system_status(),
        'timestamp': service.get_last_update_time(),
    }
    
    return JsonResponse(data)
