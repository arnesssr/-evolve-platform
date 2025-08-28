"""
Admin Finance Reports API Views
Provides endpoints for generating financial reports and analytics.
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

from App.admin.services.revenue_service import RevenueService
from App.admin.services.commissions_service import CommissionsService
from App.admin.services.invoices_service import InvoicesService
from App.admin.services.payouts_service import PayoutsService
from App.admin.services.transactions_service import TransactionsService
from App.admin.services.audit_service import AuditService
from App.admin.models.scheduled_report import ScheduledReport


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class ReportsGenerateView(View):
    """Generate financial reports"""
    
    def __init__(self):
        super().__init__()
        self.revenue_service = RevenueService()
        self.commissions_service = CommissionsService()
        self.invoices_service = InvoicesService()
        self.payouts_service = PayoutsService()
        self.transactions_service = TransactionsService()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            report_type = data.get('type')
            parameters = data.get('parameters', {})
            
            if not report_type:
                return JsonResponse({
                    'success': False,
                    'error': 'Report type is required'
                }, status=400)
            
            # Parse common parameters
            start_date = parameters.get('start_date')
            end_date = parameters.get('end_date')
            format_type = parameters.get('format', 'pdf')  # pdf, xlsx, csv
            
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            report_data = None
            
            # Generate different types of reports
            if report_type == 'revenue_summary':
                report_data = self._generate_revenue_summary_report(
                    start_date, end_date, parameters
                )
            elif report_type == 'commission_report':
                report_data = self._generate_commission_report(
                    start_date, end_date, parameters
                )
            elif report_type == 'payout_report':
                report_data = self._generate_payout_report(
                    start_date, end_date, parameters
                )
            elif report_type == 'financial_overview':
                report_data = self._generate_financial_overview(
                    start_date, end_date, parameters
                )
            elif report_type == 'cash_flow_statement':
                report_data = self._generate_cash_flow_statement(
                    start_date, end_date, parameters
                )
            elif report_type == 'reseller_performance':
                report_data = self._generate_reseller_performance_report(
                    start_date, end_date, parameters
                )
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown report type: {report_type}'
                }, status=400)
            
            # Log audit trail
            self.audit_service.log(
                action='report_generate',
                actor_id=request.user.id,
                target_type='report',
                target_id='',
                details={
                    'report_type': report_type,
                    'parameters': parameters,
                    'format': format_type
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'report_type': report_type,
                    'generated_at': datetime.now().isoformat(),
                    'download_url': report_data['download_url'],
                    'filename': report_data['filename'],
                    'file_size': report_data['file_size'],
                    'format': format_type,
                    'expires_at': report_data['expires_at']
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def _generate_revenue_summary_report(self, start_date, end_date, parameters):
        """Generate revenue summary report"""
        metrics = self.revenue_service.get_revenue_metrics(start_date, end_date)
        trends = self.revenue_service.get_revenue_trends(
            start_date, end_date, parameters.get('interval', 'monthly')
        )
        
        report_data = {
            'title': 'Revenue Summary Report',
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'metrics': metrics,
            'trends': trends,
            'generated_at': datetime.now().isoformat()
        }
        
        return self._format_report(report_data, parameters.get('format', 'pdf'))
    
    def _generate_commission_report(self, start_date, end_date, parameters):
        """Generate commission report"""
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        if parameters.get('reseller_id'):
            filters['reseller_id'] = parameters['reseller_id']
        if parameters.get('status'):
            filters['status'] = parameters['status']
        
        commissions_data = self.commissions_service.get_commissions_list(
            page=1, page_size=1000, filters=filters
        )
        
        report_data = {
            'title': 'Commission Report',
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'commissions': commissions_data['results'],
            'summary': commissions_data['summary'],
            'generated_at': datetime.now().isoformat()
        }
        
        return self._format_report(report_data, parameters.get('format', 'pdf'))
    
    def _generate_payout_report(self, start_date, end_date, parameters):
        """Generate payout report"""
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        if parameters.get('reseller_id'):
            filters['reseller_id'] = parameters['reseller_id']
        if parameters.get('status'):
            filters['status'] = parameters['status']
        
        payouts_data = self.payouts_service.get_payouts_list(
            page=1, page_size=1000, filters=filters
        )
        
        report_data = {
            'title': 'Payout Report',
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'payouts': payouts_data['results'],
            'summary': payouts_data['summary'],
            'generated_at': datetime.now().isoformat()
        }
        
        return self._format_report(report_data, parameters.get('format', 'pdf'))
    
    def _generate_financial_overview(self, start_date, end_date, parameters):
        """Generate comprehensive financial overview"""
        # Get data from all services
        revenue_metrics = self.revenue_service.get_revenue_metrics(start_date, end_date)
        
        commission_filters = {'start_date': start_date, 'end_date': end_date}
        commissions_data = self.commissions_service.get_commissions_list(
            page=1, page_size=10, filters=commission_filters
        )
        
        payout_filters = {'start_date': start_date, 'end_date': end_date}
        payouts_data = self.payouts_service.get_payouts_list(
            page=1, page_size=10, filters=payout_filters
        )
        
        transaction_filters = {'start_date': start_date, 'end_date': end_date}
        transactions_data = self.transactions_service.get_transactions_list(
            page=1, page_size=10, filters=transaction_filters
        )
        
        report_data = {
            'title': 'Financial Overview',
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'revenue': revenue_metrics,
            'commissions': commissions_data['summary'],
            'payouts': payouts_data['summary'],
            'transactions': transactions_data['summary'],
            'generated_at': datetime.now().isoformat()
        }
        
        return self._format_report(report_data, parameters.get('format', 'pdf'))
    
    def _generate_cash_flow_statement(self, start_date, end_date, parameters):
        """Generate cash flow statement"""
        cash_flow = self.transactions_service.get_cash_flow_analysis(
            start_date, end_date, parameters.get('interval', 'monthly'), 0
        )
        
        report_data = {
            'title': 'Cash Flow Statement',
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'cash_flow': cash_flow,
            'generated_at': datetime.now().isoformat()
        }
        
        return self._format_report(report_data, parameters.get('format', 'pdf'))
    
    def _generate_reseller_performance_report(self, start_date, end_date, parameters):
        """Generate reseller performance report"""
        # This would typically aggregate data across multiple resellers
        # For now, return a placeholder structure
        report_data = {
            'title': 'Reseller Performance Report',
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'resellers': [],  # Would be populated with actual performance data
            'generated_at': datetime.now().isoformat()
        }
        
        return self._format_report(report_data, parameters.get('format', 'pdf'))
    
    def _format_report(self, report_data, format_type):
        """Format report data into requested format"""
        # This is a simplified implementation
        # In production, you'd use proper report generation libraries
        
        filename = f"{report_data['title'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
        
        # Generate a mock download URL
        download_url = f"/platform/admin/api/v1/finance/reports/download/{filename}/"
        
        return {
            'download_url': download_url,
            'filename': filename,
            'file_size': 1024 * 50,  # Mock file size
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class ReportsPreviewView(View):
    """Preview report data before generation"""
    
    def __init__(self):
        super().__init__()
        self.revenue_service = RevenueService()
        self.commissions_service = CommissionsService()
        self.payouts_service = PayoutsService()
        self.transactions_service = TransactionsService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            report_type = data.get('type')
            parameters = data.get('parameters', {})
            
            if not report_type:
                return JsonResponse({
                    'success': False,
                    'error': 'Report type is required'
                }, status=400)
            
            # Parse common parameters
            start_date = parameters.get('start_date')
            end_date = parameters.get('end_date')
            
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Generate preview data (limited dataset)
            preview_data = {}
            
            if report_type == 'revenue_summary':
                preview_data = {
                    'metrics': self.revenue_service.get_revenue_metrics(start_date, end_date),
                    'record_count': 'N/A'
                }
            elif report_type == 'commission_report':
                filters = {'start_date': start_date, 'end_date': end_date}
                commissions_preview = self.commissions_service.get_commissions_list(
                    page=1, page_size=5, filters=filters
                )
                preview_data = {
                    'sample_records': commissions_preview['results'][:5],
                    'record_count': commissions_preview['total_count']
                }
            elif report_type == 'payout_report':
                filters = {'start_date': start_date, 'end_date': end_date}
                payouts_preview = self.payouts_service.get_payouts_list(
                    page=1, page_size=5, filters=filters
                )
                preview_data = {
                    'sample_records': payouts_preview['results'][:5],
                    'record_count': payouts_preview['total_count']
                }
            elif report_type == 'financial_overview':
                # Light preview: just revenue metrics summary
                preview_data = {
                    'metrics': self.revenue_service.get_revenue_metrics(start_date, end_date),
                    'record_count': 'N/A'
                }
            elif report_type == 'cash_flow_statement':
                cf = self.transactions_service.get_cash_flow_analysis(
                    start_date, end_date, 'monthly', 0
                )
                preview_data = {
                    'sample_records': cf.get('historical', [])[:5],
                    'record_count': len(cf.get('historical', []))
                }
            
            return JsonResponse({
                'success': True,
                'data': {
                    'report_type': report_type,
                    'preview': preview_data,
                    'estimated_size': f"{preview_data.get('record_count', 0)} records"
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required], name='dispatch')
class ReportsDownloadView(View):
    """Download generated report"""
    
    def get(self, request, filename):
        try:
            # This is a placeholder implementation
            # In production, you'd retrieve the actual file from storage
            
            # Mock file content based on filename
            if filename.endswith('.pdf'):
                content_type = 'application/pdf'
                content = b'Mock PDF content'
            elif filename.endswith('.xlsx'):
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                content = b'Mock Excel content'
            elif filename.endswith('.csv'):
                content_type = 'text/csv'
                content = b'Mock CSV content'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid file format'
                }, status=400)
            
            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class ReportsScheduleView(View):
    """Schedule automated report generation"""
    
    def __init__(self):
        super().__init__()
        self.audit_service = AuditService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            required_fields = ['report_type', 'schedule', 'recipients']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)
            
            # Create scheduled report configuration
            schedule_data = {
                'report_type': data['report_type'],
                'schedule': data['schedule'],  # cron expression or interval
                'recipients': data['recipients'],  # email list
                'parameters': data.get('parameters', {}),
                'format': data.get('format', 'pdf'),
                'active': data.get('active', True),
                'created_by': request.user.id,
                'created_at': datetime.now().isoformat()
            }
            
            # Persist scheduled report
            sched = ScheduledReport(
                report_type=data['report_type'],
                schedule=data['schedule'],
                recipients=data.get('recipients', []),
                parameters=data.get('parameters', {}),
                format=data.get('format', 'pdf'),
                active=data.get('active', True),
                created_by=request.user
            )
            # Initialize next_run_at based on cron
            try:
                from App.admin.services.scheduler_service import compute_next_run
                from django.utils import timezone as dj_tz
                nxt = compute_next_run(sched.schedule)
                if nxt:
                    sched.next_run_at = dj_tz.make_aware(nxt, dj_tz.get_current_timezone())
            except Exception:
                pass
            sched.save()
            
            # Log audit trail
            self.audit_service.log(
                action='report_schedule',
                actor_id=request.user.id,
                target_type='scheduled_report',
                target_id=sched.id,
                details={
                    'report_type': sched.report_type,
                    'schedule': sched.schedule,
                    'recipients_count': len(sched.recipients)
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'schedule_id': sched.id,
                    'report_type': sched.report_type,
                    'schedule': sched.schedule,
                    'next_run': sched.next_run_at.isoformat() if sched.next_run_at else None,
                    'status': 'active' if sched.active else 'inactive'
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def get(self, request):
        """List scheduled reports"""
        try:
            # Fetch from database
            qs = ScheduledReport.objects.all().order_by('-created_at')
            scheduled_reports = []
            for s in qs:
                scheduled_reports.append({
                    'id': s.id,
                    'report_type': s.report_type,
                    'schedule': s.schedule,
                    'format': s.format,
                    'recipients': s.recipients,
                    'last_run': s.last_run_at.isoformat() if s.last_run_at else None,
                    'next_run': s.next_run_at.isoformat() if s.next_run_at else None,
                    'status': 'active' if s.active else 'inactive',
                    'created_at': s.created_at.isoformat(),
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'scheduled_reports': scheduled_reports,
                    'total_count': qs.count()
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
