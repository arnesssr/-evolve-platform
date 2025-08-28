"""
Admin Finance Invoices API Views
Provides endpoints for invoice management, generation, and operations.
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

from App.admin.services.invoices_service import InvoicesService
from App.admin.services.audit_service import AuditService


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class InvoicesListView(View):
    """Invoices list with filtering and pagination"""
    
    def __init__(self):
        super().__init__()
        self.invoices_service = InvoicesService()
        self.audit_service = AuditService()
    
    def get(self, request):
        try:
            # Parse query parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 25))
            status = request.GET.get('status')
            business_id = request.GET.get('business_id')
            reseller_id = request.GET.get('reseller_id')
            min_amount = request.GET.get('min_amount')
            max_amount = request.GET.get('max_amount')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            search = request.GET.get('search')
            invoice_type = request.GET.get('invoice_type')
            
            # Build filters
            filters = {}
            if status:
                filters['status'] = status
            if business_id:
                filters['business_id'] = business_id
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
            if invoice_type:
                filters['invoice_type'] = invoice_type
            
            # Get filtered invoices
            invoices_data = self.invoices_service.get_invoices_list(
                page=page, 
                page_size=page_size, 
                filters=filters
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'invoices': invoices_data['results'],
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': invoices_data['total_count'],
                        'total_pages': invoices_data['total_pages'],
                        'has_next': invoices_data['has_next'],
                        'has_previous': invoices_data['has_previous']
                    },
                    'summary': {
                        'total_amount': invoices_data['summary']['total_amount'],
                        'draft_count': invoices_data['summary']['draft_count'],
                        'sent_count': invoices_data['summary']['sent_count'],
                        'paid_count': invoices_data['summary']['paid_count'],
                        'overdue_count': invoices_data['summary']['overdue_count']
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class InvoicesCreateView(View):
    """Create invoice from approved commissions or manually"""
    
    def __init__(self):
        super().__init__()
        self.invoices_service = InvoicesService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            creation_type = data.get('type', 'manual')  # 'manual' or 'from_commissions'
            
            if creation_type == 'from_commissions':
                commission_ids = data.get('commission_ids', [])
                if not commission_ids:
                    return JsonResponse({
                        'success': False,
                        'error': 'Commission IDs are required'
                    }, status=400)
                
                # Create invoice from approved commissions
                invoice = self.invoices_service.create_invoice_from_commissions(
                    commission_ids=commission_ids,
                    created_by=request.user
                )
                
            else:  # manual creation
                required_fields = ['business_id', 'amount', 'description']
                missing_fields = [field for field in required_fields if not data.get(field)]
                
                if missing_fields:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required fields: {", ".join(missing_fields)}'
                    }, status=400)
                
                # Create manual invoice
                invoice = self.invoices_service.create_manual_invoice(
                    business_id=data['business_id'],
                    amount=float(data['amount']),
                    description=data['description'],
                    due_date=data.get('due_date'),
                    metadata=data.get('metadata', {}),
                    created_by=request.user
                )
            
            # Log audit trail
            self.audit_service.log_action(
                user=request.user,
                action='invoice_create',
                resource_type='invoice',
                resource_ids=[invoice.id],
                details={
                    'type': creation_type,
                    'amount': float(invoice.amount),
                    'business_id': invoice.business_id
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'invoice': {
                        'id': invoice.id,
                        'invoice_number': invoice.invoice_number,
                        'amount': float(invoice.amount),
                        'status': invoice.status,
                        'created_at': invoice.created_at.isoformat(),
                        'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                        'business': {
                            'id': invoice.business.id,
                            'name': invoice.business.name
                        } if invoice.business else None
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class InvoicesActionView(View):
    """Invoice actions: send, mark paid, cancel"""
    
    def __init__(self):
        super().__init__()
        self.invoices_service = InvoicesService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            invoice_ids = data.get('invoice_ids', [])
            
            if not action or not invoice_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Action and invoice_ids are required'
                }, status=400)
            
            results = []
            
            if action == 'send':
                email_template = data.get('email_template', 'default')
                results = self.invoices_service.send_invoices(
                    invoice_ids, 
                    email_template,
                    request.user
                )
            elif action == 'mark_paid':
                payment_date = data.get('payment_date')
                payment_method = data.get('payment_method', 'bank_transfer')
                reference = data.get('reference', '')
                
                results = self.invoices_service.mark_invoices_paid(
                    invoice_ids, 
                    payment_date,
                    payment_method,
                    reference,
                    request.user
                )
            elif action == 'cancel':
                reason = data.get('reason', 'Cancelled by admin')
                results = self.invoices_service.cancel_invoices(
                    invoice_ids, 
                    reason, 
                    request.user
                )
            elif action == 'regenerate':
                results = self.invoices_service.regenerate_invoices(
                    invoice_ids,
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
                action=f'invoice_{action}',
                resource_type='invoice',
                resource_ids=invoice_ids,
                details={
                    'action': action,
                    'count': len(invoice_ids),
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


@method_decorator([staff_member_required], name='dispatch')
class InvoiceDownloadView(View):
    """Download invoice PDF"""
    
    def __init__(self):
        super().__init__()
        self.invoices_service = InvoicesService()
    
    def get(self, request, invoice_id):
        try:
            # Generate or retrieve invoice PDF
            pdf_data = self.invoices_service.get_invoice_pdf(invoice_id)
            
            if not pdf_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Invoice not found'
                }, status=404)
            
            response = HttpResponse(
                pdf_data['content'],
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{pdf_data["filename"]}"'
            
            return response
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class InvoicesBulkActionView(View):
    """Bulk operations on invoices"""
    
    def __init__(self):
        super().__init__()
        self.invoices_service = InvoicesService()
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
            
            if action == 'send_filtered':
                email_template = data.get('email_template', 'default')
                results = self.invoices_service.send_filtered_invoices(
                    filters, 
                    email_template,
                    request.user
                )
            elif action == 'export_filtered':
                export_data = self.invoices_service.export_filtered_invoices(
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
                action=f'invoice_bulk_{action}',
                resource_type='invoice',
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
class InvoicesExportView(View):
    """Export invoices to CSV/XLSX"""
    
    def __init__(self):
        super().__init__()
        self.invoices_service = InvoicesService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            export_format = data.get('format', 'csv')
            filters = data.get('filters', {})
            fields = data.get('fields', [])
            
            # Generate export
            export_data = self.invoices_service.export_invoices(
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
class InvoicesDetailView(View):
    """Invoice detail view"""
    
    def __init__(self):
        super().__init__()
        self.invoices_service = InvoicesService()
    
    def get(self, request, invoice_id):
        try:
            invoice = self.invoices_service.get_invoice_detail(invoice_id)
            
            if not invoice:
                return JsonResponse({
                    'success': False,
                    'error': 'Invoice not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'invoice': invoice
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
