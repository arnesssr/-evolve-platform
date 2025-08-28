"""
Admin Finance Transactions API Views
Provides endpoints for unified transaction feed and financial analytics.
"""

import json
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator

from App.admin.services.transactions_service import TransactionsService
from App.admin.services.audit_service import AuditService


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class TransactionsListView(View):
    """Unified transactions list with filtering and pagination"""
    
    def __init__(self):
        super().__init__()
        self.transactions_service = TransactionsService()
        self.audit_service = AuditService()
    
    def get(self, request):
        try:
            # Parse query parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 25))
            transaction_type = request.GET.get('type')  # 'incoming', 'outgoing', 'internal'
            status = request.GET.get('status')
            method = request.GET.get('method')
            min_amount = request.GET.get('min_amount')
            max_amount = request.GET.get('max_amount')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            search = request.GET.get('search')
            source = request.GET.get('source')  # 'invoice', 'payout', 'commission'
            
            # Build filters
            filters = {}
            if transaction_type:
                filters['type'] = transaction_type
            if status:
                filters['status'] = status
            if method:
                filters['method'] = method
            if min_amount:
                filters['min_amount'] = float(min_amount)
            if max_amount:
                filters['max_amount'] = float(max_amount)
            if start_date:
                filters['start_date'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                filters['end_date'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if search:
                filters['search'] = search
            if source:
                filters['source'] = source
            
            # Get filtered transactions
            transactions_data = self.transactions_service.get_transactions_list(
                page=page, 
                page_size=page_size, 
                filters=filters
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'transactions': transactions_data['results'],
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': transactions_data['total_count'],
                        'total_pages': transactions_data['total_pages'],
                        'has_next': transactions_data['has_next'],
                        'has_previous': transactions_data['has_previous']
                    },
                    'summary': {
                        'total_incoming': transactions_data['summary']['total_incoming'],
                        'total_outgoing': transactions_data['summary']['total_outgoing'],
                        'total_internal': transactions_data['summary']['total_internal'],
                        'net_amount': transactions_data['summary']['net_amount'],
                        'transaction_count': transactions_data['summary']['transaction_count']
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class TransactionsMetricsView(View):
    """Transaction metrics and analytics for charts"""
    
    def __init__(self):
        super().__init__()
        self.transactions_service = TransactionsService()
    
    def get(self, request):
        try:
            # Parse date range parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            interval = request.GET.get('interval', 'daily')  # daily, weekly, monthly
            
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.now() - timedelta(days=30)
                
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.now()
            
            # Get transaction metrics
            metrics = self.transactions_service.get_transaction_metrics(
                start_date, end_date, interval
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'volume_chart': {
                        'labels': [item['period'] for item in metrics['volume_data']],
                        'datasets': [
                            {
                                'label': 'Incoming',
                                'data': [item['incoming'] for item in metrics['volume_data']],
                                'borderColor': '#4CAF50',
                                'backgroundColor': 'rgba(76, 175, 80, 0.2)',
                                'fill': True
                            },
                            {
                                'label': 'Outgoing',
                                'data': [item['outgoing'] for item in metrics['volume_data']],
                                'borderColor': '#F44336',
                                'backgroundColor': 'rgba(244, 67, 54, 0.2)',
                                'fill': True
                            },
                            {
                                'label': 'Internal',
                                'data': [item['internal'] for item in metrics['volume_data']],
                                'borderColor': '#FF9800',
                                'backgroundColor': 'rgba(255, 152, 0, 0.2)',
                                'fill': True
                            }
                        ]
                    },
                    'type_distribution': {
                        'labels': ['Incoming', 'Outgoing', 'Internal'],
                        'data': [
                            metrics['type_breakdown']['incoming'],
                            metrics['type_breakdown']['outgoing'],
                            metrics['type_breakdown']['internal']
                        ],
                        'backgroundColor': ['#4CAF50', '#F44336', '#FF9800']
                    },
                    'method_distribution': {
                        'labels': list(metrics['method_breakdown'].keys()),
                        'data': list(metrics['method_breakdown'].values()),
                        'backgroundColor': [
                            '#2196F3', '#9C27B0', '#00BCD4', 
                            '#8BC34A', '#CDDC39', '#FFC107'
                        ]
                    },
                    'summary': {
                        'total_volume': metrics['summary']['total_volume'],
                        'transaction_count': metrics['summary']['transaction_count'],
                        'avg_transaction': metrics['summary']['avg_transaction'],
                        'growth_rate': metrics['summary']['growth_rate']
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class TransactionsReconcileView(View):
    """Manual transaction reconciliation"""
    
    def __init__(self):
        super().__init__()
        self.transactions_service = TransactionsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            transaction_ids = data.get('transaction_ids', [])
            
            if not action:
                return JsonResponse({
                    'success': False,
                    'error': 'Action is required'
                }, status=400)
            
            results = []
            
            if action == 'mark_reconciled':
                reconciliation_date = data.get('reconciliation_date')
                reference = data.get('reference', '')
                notes = data.get('notes', '')
                
                results = self.transactions_service.mark_reconciled(
                    transaction_ids,
                    reconciliation_date,
                    reference,
                    notes,
                    request.user
                )
                
            elif action == 'mark_disputed':
                reason = data.get('reason', 'Disputed transaction')
                results = self.transactions_service.mark_disputed(
                    transaction_ids,
                    reason,
                    request.user
                )
                
            elif action == 'auto_reconcile':
                date_range = data.get('date_range', {})
                tolerance = data.get('tolerance', 0.01)  # $0.01 tolerance
                
                results = self.transactions_service.auto_reconcile(
                    date_range.get('start_date'),
                    date_range.get('end_date'),
                    tolerance,
                    request.user
                )
                
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown reconciliation action: {action}'
                }, status=400)
            
            # Log audit trail
            self.audit_service.log_action(
                user=request.user,
                action=f'transaction_{action}',
                resource_type='transaction',
                resource_ids=transaction_ids,
                details={
                    'action': action,
                    'count': len(transaction_ids),
                    'results': results
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'action': action,
                    'processed_count': results.get('processed_count', 0),
                    'failed_count': results.get('failed_count', 0),
                    'results': results
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class TransactionsExportView(View):
    """Export transactions to CSV/XLSX"""
    
    def __init__(self):
        super().__init__()
        self.transactions_service = TransactionsService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            export_format = data.get('format', 'csv')
            filters = data.get('filters', {})
            fields = data.get('fields', [])
            include_summary = data.get('include_summary', True)
            
            # Generate export
            export_data = self.transactions_service.export_transactions(
                filters=filters,
                format=export_format,
                fields=fields,
                include_summary=include_summary
            )
            
            if export_format == 'csv':
                response = HttpResponse(
                    export_data['content'], 
                    content_type='text/csv'
                )
                response['Content-Disposition'] = f'attachment; filename="{export_data["filename"]}"'
                return response
            else:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'download_url': export_data['url'],
                        'filename': export_data['filename'],
                        'record_count': export_data['record_count']
                    }
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required], name='dispatch')
class TransactionsDetailView(View):
    """Transaction detail view"""
    
    def __init__(self):
        super().__init__()
        self.transactions_service = TransactionsService()
    
    def get(self, request, transaction_id):
        try:
            transaction = self.transactions_service.get_transaction_detail(
                transaction_id,
                include_related=True
            )
            
            if not transaction:
                return JsonResponse({
                    'success': False,
                    'error': 'Transaction not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'transaction': transaction
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class TransactionsCashFlowView(View):
    """Cash flow analysis and projections"""
    
    def __init__(self):
        super().__init__()
        self.transactions_service = TransactionsService()
    
    def get(self, request):
        try:
            # Parse parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            interval = request.GET.get('interval', 'weekly')
            forecast_periods = int(request.GET.get('forecast_periods', 4))
            
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.now() - timedelta(days=90)
                
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.now()
            
            # Get cash flow data
            cash_flow = self.transactions_service.get_cash_flow_analysis(
                start_date, end_date, interval, forecast_periods
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'historical': cash_flow['historical'],
                    'forecast': cash_flow['forecast'],
                    'chart_data': {
                        'labels': [item['period'] for item in cash_flow['historical']] + 
                                 [item['period'] for item in cash_flow['forecast']],
                        'datasets': [
                            {
                                'label': 'Historical Cash Flow',
                                'data': [item['net_flow'] for item in cash_flow['historical']] + 
                                       [None] * len(cash_flow['forecast']),
                                'borderColor': '#2196F3',
                                'backgroundColor': 'rgba(33, 150, 243, 0.2)',
                                'fill': True
                            },
                            {
                                'label': 'Projected Cash Flow',
                                'data': [None] * len(cash_flow['historical']) + 
                                       [item['net_flow'] for item in cash_flow['forecast']],
                                'borderColor': '#FF5722',
                                'backgroundColor': 'rgba(255, 87, 34, 0.2)',
                                'borderDash': [5, 5],
                                'fill': True
                            }
                        ]
                    },
                    'summary': {
                        'avg_inflow': cash_flow['summary']['avg_inflow'],
                        'avg_outflow': cash_flow['summary']['avg_outflow'],
                        'avg_net_flow': cash_flow['summary']['avg_net_flow'],
                        'trend': cash_flow['summary']['trend'],
                        'volatility': cash_flow['summary']['volatility']
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
