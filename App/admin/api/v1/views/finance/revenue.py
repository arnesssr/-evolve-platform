"""
Admin Finance Revenue API Views
Provides endpoints for revenue metrics, source breakdowns, and forecasting.
"""

import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View

from App.admin.services.revenue_service import RevenueService
from App.admin.services.audit_service import AuditService


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class RevenueMetricsView(View):
    """Revenue metrics endpoint for dashboard KPIs"""
    
    def __init__(self):
        super().__init__()
        self.revenue_service = RevenueService()
        self.audit_service = AuditService()
    
    def get(self, request):
        try:
            # Parse date range parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.now() - timedelta(days=30)
                
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.now()
            
            # Get revenue metrics
            metrics = self.revenue_service.get_revenue_metrics(start_date, end_date)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'total_revenue': metrics.get('total_revenue', 0),
                    'mrr': metrics.get('mrr', 0),
                    'arr': metrics.get('arr', 0),
                    'growth_rate': metrics.get('growth_rate', 0),
                    'pending_commissions': metrics.get('pending_commissions', 0),
                    'processed_payouts': metrics.get('processed_payouts', 0),
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class RevenueSourceBreakdownView(View):
    """Revenue source breakdown for charts"""
    
    def __init__(self):
        super().__init__()
        self.revenue_service = RevenueService()
    
    def get(self, request):
        try:
            # Parse date range parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.now() - timedelta(days=30)
                
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.now()
            
            # Get source breakdown
            breakdown = self.revenue_service.get_source_breakdown(start_date, end_date)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'sources': breakdown.get('sources', []),
                    'chart_data': {
                        'labels': [item['name'] for item in breakdown.get('sources', [])],
                        'data': [item['amount'] for item in breakdown.get('sources', [])],
                        'backgroundColor': [
                            '#FF6384', '#36A2EB', '#FFCE56', 
                            '#4BC0C0', '#9966FF', '#FF9F40'
                        ]
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class RevenueForecastView(View):
    """Revenue forecast endpoint"""
    
    def __init__(self):
        super().__init__()
        self.revenue_service = RevenueService()
    
    def get(self, request):
        try:
            # Parse forecast parameters
            periods = int(request.GET.get('periods', 12))  # Default 12 months
            method = request.GET.get('method', 'moving_average')  # Default method
            
            # Get forecast data
            forecast = self.revenue_service.get_revenue_forecast(periods, method)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'forecast': forecast.get('forecast', []),
                    'historical': forecast.get('historical', []),
                    'chart_data': {
                        'labels': [item['period'] for item in forecast.get('forecast', [])],
                        'datasets': [
                            {
                                'label': 'Historical Revenue',
                                'data': [item['amount'] for item in forecast.get('historical', [])],
                                'borderColor': '#36A2EB',
                                'backgroundColor': '#36A2EB'
                            },
                            {
                                'label': 'Forecast',
                                'data': [item['amount'] for item in forecast.get('forecast', [])],
                                'borderColor': '#FF6384',
                                'backgroundColor': '#FF6384',
                                'borderDash': [5, 5]
                            }
                        ]
                    },
                    'confidence': forecast.get('confidence', 0.8),
                    'method': method
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class RevenueTrendsView(View):
    """Revenue trends over time for charts"""
    
    def __init__(self):
        super().__init__()
        self.revenue_service = RevenueService()
    
    def get(self, request):
        try:
            # Parse parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            interval = request.GET.get('interval', 'monthly')  # daily, weekly, monthly
            
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.now() - timedelta(days=365)
                
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.now()
            
            # Get trends data
            trends = self.revenue_service.get_revenue_trends(start_date, end_date, interval)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'trends': trends.get('trends', []),
                    'chart_data': {
                        'labels': [item['period'] for item in trends.get('trends', [])],
                        'datasets': [
                            {
                                'label': 'Revenue',
                                'data': [item['revenue'] for item in trends.get('trends', [])],
                                'borderColor': '#36A2EB',
                                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                                'fill': True
                            },
                            {
                                'label': 'Commissions',
                                'data': [item['commissions'] for item in trends.get('trends', [])],
                                'borderColor': '#FF6384',
                                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                                'fill': True
                            }
                        ]
                    },
                    'summary': {
                        'total_periods': len(trends.get('trends', [])),
                        'avg_revenue': trends.get('avg_revenue', 0),
                        'growth_trend': trends.get('growth_trend', 'stable')
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
