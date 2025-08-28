"""
Admin Finance Payouts API Views
Provides endpoints for payout management and processing operations.
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

from App.admin.services.payouts_service import PayoutsService
from App.admin.services.audit_service import AuditService


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class PayoutsListView(View):
    """Payouts list with filtering and pagination"""
    
    def __init__(self):
        super().__init__()
        self.payouts_service = PayoutsService()
        self.audit_service = AuditService()
    
    def get(self, request):
        try:
            # Parse query parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 25))
            status = request.GET.get('status')
            reseller_id = request.GET.get('reseller_id')
            method = request.GET.get('method')
            min_amount = request.GET.get('min_amount')
            max_amount = request.GET.get('max_amount')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            search = request.GET.get('search')
            
            # Build filters
            filters = {}
            if status:
                filters['status'] = status
            if reseller_id:
                filters['reseller_id'] = reseller_id
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
            
            # Get filtered payouts
            payouts_data = self.payouts_service.get_payouts_list(
                page=page, 
                page_size=page_size, 
                filters=filters
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'payouts': payouts_data['results'],
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': payouts_data['total_count'],
                        'total_pages': payouts_data['total_pages'],
                        'has_next': payouts_data['has_next'],
                        'has_previous': payouts_data['has_previous']
                    },
                    'summary': {
                        'total_amount': payouts_data['summary']['total_amount'],
                        'pending_count': payouts_data['summary']['pending_count'],
                        'processing_count': payouts_data['summary']['processing_count'],
                        'completed_count': payouts_data['summary']['completed_count'],
                        'failed_count': payouts_data['summary']['failed_count']
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class PayoutsActionView(View):
    """Payout actions: process, complete, fail, retry"""
    
    def __init__(self):
        super().__init__()
        self.payouts_service = PayoutsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            payout_ids = data.get('payout_ids', [])
            
            if not action or not payout_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Action and payout_ids are required'
                }, status=400)
            
            results = []
            
            if action == 'process':
                payment_method = data.get('payment_method', 'bank_transfer')
                results = self.payouts_service.process_payouts(
                    payout_ids, 
                    payment_method,
                    request.user
                )
            elif action == 'complete':
                transaction_id = data.get('transaction_id')
                completion_date = data.get('completion_date')
                results = self.payouts_service.complete_payouts(
                    payout_ids, 
                    transaction_id,
                    completion_date,
                    request.user
                )
            elif action == 'fail':
                reason = data.get('reason', 'Processing failed')
                results = self.payouts_service.fail_payouts(
                    payout_ids, 
                    reason, 
                    request.user
                )
            elif action == 'retry':
                results = self.payouts_service.retry_payouts(
                    payout_ids,
                    request.user
                )
            elif action == 'cancel':
                reason = data.get('reason', 'Cancelled by admin')
                results = self.payouts_service.cancel_payouts(
                    payout_ids,
                    reason,
                    request.user
                )
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown action: {action}'
                }, status=400)
            
            # Log audit trail
            self.audit_service.log_action(
                user=request.user,
                action=f'payout_{action}',
                resource_type='payout',
                resource_ids=payout_ids,
                details={
                    'action': action,
                    'count': len(payout_ids),
                    'results': results
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'action': action,
                    'processed_count': len([r for r in results if r.get('success')]),
                    'failed_count': len([r for r in results if not r.get('success')]),
                    'results': results
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class PayoutsBulkActionView(View):
    """Bulk operations on payouts"""
    
    def __init__(self):
        super().__init__()
        self.payouts_service = PayoutsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            filters = data.get('filters', {})
            
            if not action:
                return JsonResponse({
                    'success': False,
                    'error': 'Action is required'
                }, status=400)
            
            if action == 'process_filtered':
                payment_method = data.get('payment_method', 'bank_transfer')
                results = self.payouts_service.process_filtered_payouts(
                    filters, 
                    payment_method,
                    request.user
                )
            elif action == 'export_filtered':
                export_data = self.payouts_service.export_filtered_payouts(
                    filters
                )
                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'export_url': export_data['url'],
                        'filename': export_data['filename'],
                        'record_count': export_data['record_count']
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown bulk action: {action}'
                }, status=400)
            
            # Log audit trail
            self.audit_service.log_action(
                user=request.user,
                action=f'payout_bulk_{action}',
                resource_type='payout',
                details={
                    'action': action,
                    'filters': filters,
                    'results': results
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'action': action,
                    'processed_count': results.get('processed_count', 0),
                    'failed_count': results.get('failed_count', 0)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class PayoutsCreateView(View):
    """Create new payout"""
    
    def __init__(self):
        super().__init__()
        self.payouts_service = PayoutsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            required_fields = ['reseller_id', 'amount', 'method']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)
            
            # Create payout
            payout = self.payouts_service.create_payout(
                reseller_id=data['reseller_id'],
                amount=float(data['amount']),
                method=data['method'],
                description=data.get('description', ''),
                payment_details=data.get('payment_details', {}),
                created_by=request.user
            )
            
            # Log audit trail
            self.audit_service.log_action(
                user=request.user,
                action='payout_create',
                resource_type='payout',
                resource_ids=[payout.id],
                details={
                    'amount': float(payout.amount),
                    'reseller_id': payout.reseller_id,
                    'method': payout.method
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'payout': {
                        'id': payout.id,
                        'amount': float(payout.amount),
                        'method': payout.method,
                        'status': payout.status,
                        'created_at': payout.created_at.isoformat(),
                        'reseller': {
                            'id': payout.reseller.id,
                            'name': payout.reseller.name
                        } if payout.reseller else None
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class PayoutsExportView(View):
    """Export payouts to CSV/XLSX"""
    
    def __init__(self):
        super().__init__()
        self.payouts_service = PayoutsService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            export_format = data.get('format', 'csv')
            filters = data.get('filters', {})
            fields = data.get('fields', [])
            
            # Generate export
            export_data = self.payouts_service.export_payouts(
                filters=filters,
                format=export_format,
                fields=fields
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
class PayoutsDetailView(View):
    """Payout detail view"""
    
    def __init__(self):
        super().__init__()
        self.payouts_service = PayoutsService()
    
    def get(self, request, payout_id):
        try:
            payout = self.payouts_service.get_payout_detail(payout_id)
            
            if not payout:
                return JsonResponse({
                    'success': False,
                    'error': 'Payout not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'payout': payout
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class PayoutsBatchView(View):
    """Create batch payout for multiple resellers"""
    
    def __init__(self):
        super().__init__()
        self.payouts_service = PayoutsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            batch_type = data.get('type', 'commission_based')  # 'commission_based' or 'manual'
            
            if batch_type == 'commission_based':
                # Create payouts from approved commissions
                min_amount = data.get('min_amount', 0)
                reseller_ids = data.get('reseller_ids', [])
                
                results = self.payouts_service.create_commission_based_payouts(
                    min_amount=min_amount,
                    reseller_ids=reseller_ids,
                    created_by=request.user
                )
                
            else:  # manual batch
                payouts_data = data.get('payouts', [])
                if not payouts_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Payouts data is required for manual batch'
                    }, status=400)
                
                results = self.payouts_service.create_manual_batch_payouts(
                    payouts_data=payouts_data,
                    created_by=request.user
                )
            
            # Log audit trail
            self.audit_service.log_action(
                user=request.user,
                action='payout_batch_create',
                resource_type='payout',
                details={
                    'type': batch_type,
                    'created_count': results.get('created_count', 0),
                    'failed_count': results.get('failed_count', 0)
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'batch_type': batch_type,
                    'created_count': results.get('created_count', 0),
                    'failed_count': results.get('failed_count', 0),
                    'total_amount': results.get('total_amount', 0),
                    'payout_ids': results.get('payout_ids', [])
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
