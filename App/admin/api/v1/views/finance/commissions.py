"""
Admin Finance Commissions API Views
Provides endpoints for commission management, bulk operations, and exports.
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

from App.admin.services.commissions_service import CommissionsService
from App.admin.services.audit_service import AuditService


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class CommissionsListView(View):
    """Commissions list with filtering and pagination"""
    
    def __init__(self):
        super().__init__()
        self.commissions_service = CommissionsService()
        self.audit_service = AuditService()
    
    def get(self, request):
        try:
            # Parse query parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 25))
            status = request.GET.get('status')
            reseller_id = request.GET.get('reseller_id')
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
            
            # Get filtered commissions
            commissions_data = self.commissions_service.get_commissions_list(
                page=page, 
                page_size=page_size, 
                filters=filters
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'commissions': commissions_data['results'],
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': commissions_data['total_count'],
                        'total_pages': commissions_data['total_pages'],
                        'has_next': commissions_data['has_next'],
                        'has_previous': commissions_data['has_previous']
                    },
                    'summary': {
                        'total_amount': commissions_data['summary']['total_amount'],
                        'pending_count': commissions_data['summary']['pending_count'],
                        'approved_count': commissions_data['summary']['approved_count'],
                        'paid_count': commissions_data['summary']['paid_count']
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class CommissionsActionView(View):
    """Commission actions: approve, reject, pay"""
    
    def __init__(self):
        super().__init__()
        self.commissions_service = CommissionsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            commission_ids = data.get('commission_ids', [])
            
            if not action or not commission_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Action and commission_ids are required'
                }, status=400)
            
            results = []
            
            if action == 'approve':
                results = self.commissions_service.approve_commissions(
                    commission_ids, 
                    request.user
                )
            elif action == 'reject':
                reason = data.get('reason', 'No reason provided')
                results = self.commissions_service.reject_commissions(
                    commission_ids, 
                    reason, 
                    request.user
                )
            elif action == 'pay':
                payment_method = data.get('payment_method', 'bank_transfer')
                results = self.commissions_service.pay_commissions(
                    commission_ids, 
                    payment_method, 
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
                action=f'commission_{action}',
                resource_type='commission',
                resource_ids=commission_ids,
                details={
                    'action': action,
                    'count': len(commission_ids),
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
class CommissionsBulkActionView(View):
    """Bulk operations on commissions"""
    
    def __init__(self):
        super().__init__()
        self.commissions_service = CommissionsService()
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
            
            if action == 'approve_filtered':
                results = self.commissions_service.approve_filtered_commissions(
                    filters, 
                    request.user
                )
            elif action == 'export_filtered':
                export_data = self.commissions_service.export_filtered_commissions(
                    filters
                )
                
                # Return export file or URL
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
                action=f'commission_bulk_{action}',
                resource_type='commission',
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
class CommissionsCreateView(View):
    """Create new commission"""
    
    def __init__(self):
        super().__init__()
        self.commissions_service = CommissionsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            required_fields = ['reseller_id', 'amount', 'commission_type']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)
            
            # Create commission
            commission = self.commissions_service.create_commission(
                reseller_id=data['reseller_id'],
                amount=float(data['amount']),
                commission_type=data['commission_type'],
                description=data.get('description', ''),
                metadata=data.get('metadata', {}),
                created_by=request.user
            )
            
            # Log audit trail
            self.audit_service.log_action(
                user=request.user,
                action='commission_create',
                resource_type='commission',
                resource_ids=[commission.id],
                details={
                    'amount': commission.amount,
                    'reseller_id': commission.reseller_id,
                    'commission_type': commission.commission_type
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'commission': {
                        'id': commission.id,
                        'amount': float(commission.amount),
                        'status': commission.status,
                        'commission_type': commission.commission_type,
                        'created_at': commission.created_at.isoformat(),
                        'reseller': {
                            'id': commission.reseller.id,
                            'name': commission.reseller.name
                        } if commission.reseller else None
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class CommissionsExportView(View):
    """Export commissions to CSV/XLSX"""
    
    def __init__(self):
        super().__init__()
        self.commissions_service = CommissionsService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            export_format = data.get('format', 'csv')
            filters = data.get('filters', {})
            fields = data.get('fields', [])
            
            # Generate export
            export_data = self.commissions_service.export_commissions(
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
class CommissionsDetailView(View):
    """Commission detail view"""
    
    def __init__(self):
        super().__init__()
        self.commissions_service = CommissionsService()
    
    def get(self, request, commission_id):
        try:
            commission = self.commissions_service.get_commission_detail(commission_id)
            
            if not commission:
                return JsonResponse({
                    'success': False,
                    'error': 'Commission not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'commission': commission
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
