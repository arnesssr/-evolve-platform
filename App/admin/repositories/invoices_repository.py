"""Admin Invoices Repository - Uses real Invoice model"""

from typing import Dict, List, Any
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from App.reseller.earnings.models.invoice import Invoice
from App.reseller.earnings.models.base import InvoiceStatusChoices


class InvoicesRepository:
    def get_invoices_list(self, page: int, page_size: int, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get paginated invoice list with filters"""
        try:
            queryset = Invoice.objects.all().select_related('reseller')

            # Apply basic filters
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('reseller_id'):
                queryset = queryset.filter(reseller_id=filters['reseller_id'])
            if filters.get('min_amount'):
                queryset = queryset.filter(total_amount__gte=filters['min_amount'])
            if filters.get('max_amount'):
                queryset = queryset.filter(total_amount__lte=filters['max_amount'])
            if filters.get('start_date'):
                queryset = queryset.filter(issue_date__gte=filters['start_date'])
            if filters.get('end_date'):
                queryset = queryset.filter(issue_date__lte=filters['end_date'])
            if filters.get('search'):
                s = filters['search']
                queryset = queryset.filter(Q(invoice_number__icontains=s) | Q(description__icontains=s))

            paginator = Paginator(queryset.order_by('-issue_date', '-invoice_number'), page_size)
            page_obj = paginator.get_page(page)

            results = []
            for inv in page_obj.object_list:
                results.append({
                    'id': inv.id,
                    'invoice_number': inv.invoice_number,
                    'amount': float(inv.total_amount),
                    'status': inv.status,
                    'issue_date': inv.issue_date.isoformat() if inv.issue_date else None,
                    'due_date': inv.due_date.isoformat() if inv.due_date else None,
                    'reseller': {
                        'id': inv.reseller.id,
                        'name': inv.reseller.company_name or inv.reseller.user.get_full_name() or inv.reseller.user.username
                    } if inv.reseller_id else None
                })

            summary_qs = queryset
            summary = summary_qs.aggregate(
                total_amount=Sum('total_amount'),
                draft_count=Count('id', filter=Q(status=InvoiceStatusChoices.DRAFT)),
                sent_count=Count('id', filter=Q(status=InvoiceStatusChoices.SENT)),
                paid_count=Count('id', filter=Q(status=InvoiceStatusChoices.PAID)),
                overdue_count=Count('id', filter=Q(status=InvoiceStatusChoices.OVERDUE)),
            )

            return {
                'results': results,
                'total_count': paginator.count,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'summary': {
                    'draft_count': summary['draft_count'] or 0,
                    'sent_count': summary['sent_count'] or 0,
                    'paid_count': summary['paid_count'] or 0,
                    'overdue_count': summary['overdue_count'] or 0,
                    'total_amount': float(summary['total_amount'] or 0)
                }
            }
        except Exception as e:
            raise Exception(f"Error getting invoices list: {str(e)}")

    def get_invoice_ids_by_filters(self, filters: Dict[str, Any]) -> List[int]:
        """Get invoice IDs matching filters"""
        qs = Invoice.objects.all()
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        if filters.get('reseller_id'):
            qs = qs.filter(reseller_id=filters['reseller_id'])
        if filters.get('start_date'):
            qs = qs.filter(issue_date__gte=filters['start_date'])
        if filters.get('end_date'):
            qs = qs.filter(issue_date__lte=filters['end_date'])
        return list(qs.values_list('id', flat=True))

    def export_invoices(self, filters: Dict[str, Any], format: str, fields: List[str]) -> Dict[str, Any]:
        """Export invoices (CSV response content for now)"""
        import csv, io
        qs = Invoice.objects.all()
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Invoice #', 'Amount', 'Status', 'Issue Date', 'Due Date'])
        for inv in qs:
            writer.writerow([inv.id, inv.invoice_number, inv.total_amount, inv.status, inv.issue_date, inv.due_date])
        return {'content': output.getvalue(), 'filename': 'invoices.csv', 'record_count': qs.count()}

    def get_invoice_detail(self, invoice_id: int) -> Dict[str, Any]:
        """Get invoice detail"""
        try:
            inv = Invoice.objects.select_related('reseller').get(id=invoice_id)
            return {
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'amount': float(inv.total_amount),
                'status': inv.status,
                'issue_date': inv.issue_date.isoformat() if inv.issue_date else None,
                'due_date': inv.due_date.isoformat() if inv.due_date else None,
                'payment_date': inv.payment_date.isoformat() if inv.payment_date else None,
                'reseller': {
                    'id': inv.reseller.id,
                    'name': inv.reseller.company_name or inv.reseller.user.get_full_name() or inv.reseller.user.username
                } if inv.reseller_id else None,
                'description': inv.description,
                'notes': inv.notes,
            }
        except Invoice.DoesNotExist:
            return {}
        except Exception as e:
            raise Exception(f"Error getting invoice detail: {str(e)}")
