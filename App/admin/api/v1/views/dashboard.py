"""
Admin Dashboard API Views
REST API endpoints for dashboard data
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ....services.dashboard_service import DashboardService
from ..serializers.dashboard import (
    DashboardMetricsSerializer,
    RecentActivitySerializer,
    SystemStatusSerializer,
    QuickStatsSerializer,
    GrowthTrendSerializer,
    DashboardFilterSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@staff_member_required
def dashboard_metrics_api(request):
    """
    Get dashboard metrics with optional filtering
    """
    try:
        # Validate filter parameters
        filter_serializer = DashboardFilterSerializer(data=request.GET)
        if not filter_serializer.is_valid():
            return Response(
                {'error': 'Invalid filter parameters', 'details': filter_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get service and fetch metrics
        service = DashboardService()
        filter_data = filter_serializer.validated_data
        
        metrics = service.get_dashboard_metrics(
            period=filter_data.get('period', 'last_7_days'),
            date_from=filter_data.get('date_from'),
            date_to=filter_data.get('date_to')
        )
        
        # Serialize response
        serializer = DashboardMetricsSerializer(metrics)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch dashboard metrics', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@staff_member_required
def recent_activities_api(request):
    """
    Get recent admin activities
    """
    try:
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 50)  # Cap at 50 activities
        
        service = DashboardService()
        activities = service.get_recent_activities(limit=limit)
        
        serializer = RecentActivitySerializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch recent activities', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@staff_member_required
def system_status_api(request):
    """
    Get system status information
    """
    try:
        service = DashboardService()
        status_data = service.get_system_status()
        
        serializer = SystemStatusSerializer(status_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch system status', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@staff_member_required
def quick_stats_api(request):
    """
    Get quick statistics for dashboard widgets
    """
    try:
        service = DashboardService()
        stats = service.get_quick_stats()
        
        serializer = QuickStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch quick stats', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@staff_member_required
def growth_trends_api(request):
    """
    Get growth trends data
    """
    try:
        days = int(request.GET.get('days', 30))
        days = min(days, 365)  # Cap at 365 days
        
        service = DashboardService()
        trends = service.get_growth_trends(days=days)
        
        serializer = GrowthTrendSerializer(trends)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch growth trends', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@staff_member_required
def dashboard_summary_api(request):
    """
    Get a comprehensive dashboard summary
    Combines multiple data sources for dashboard overview
    """
    try:
        service = DashboardService()
        
        # Get all dashboard data
        summary = {
            'metrics': service.get_dashboard_metrics(),
            'quick_stats': service.get_quick_stats(),
            'system_status': service.get_system_status(),
            'recent_activities': service.get_recent_activities(limit=5),
            'last_updated': service.get_last_update_time(),
        }
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to fetch dashboard summary', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@staff_member_required
@csrf_exempt
def refresh_dashboard_cache(request):
    """
    Force refresh dashboard cache
    """
    try:
        from django.core.cache import cache
        
        # Clear dashboard-related cache keys
        cache_keys = [
            'dashboard_metrics_*',
            'dashboard_quick_stats',
        ]
        
        for key_pattern in cache_keys:
            cache.delete_pattern(key_pattern)
        
        return Response(
            {'message': 'Dashboard cache refreshed successfully'},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {'error': 'Failed to refresh cache', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
