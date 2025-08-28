"""Admin Payouts Repository - Uses real Payout model"""

from typing import Dict, List, Any
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from App.reseller.earnings.models.payout import Payout
from App.reseller.earnings.models.base import PayoutStatusChoices


class PayoutsRepository:
    def get_payouts_list(self, page: int, page_size: int, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get paginated payout list with filters"""
        try:
            queryset = Payout.objects.all().select_related('reseller')

            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('reseller_id'):
                queryset = queryset.filter(reseller_id=filters['reseller_id'])
            if filters.get('method'):
                queryset = queryset.filter(payment_method=filters['method'])
            if filters.get('min_amount'):
                queryset = queryset.filter(amount__gte=filters['min_amount'])
            if filters.get('max_amount'):
                queryset = queryset.filter(amount__lte=filters['max_amount'])
            if filters.get('start_date'):
                queryset = queryset.filter(request_date__gte=filters['start_date'])
            if filters.get('end_date'):
                queryset = queryset.filter(request_date__lte=filters['end_date'])

            paginator = Paginator(queryset.order_by('-request_date'), page_size)
            page_obj = paginator.get_page(page)

            results = []
            for p in page_obj.object_list:
                results.append({
                    'id': p.id,
                    'amount': float(p.amount),
                    'method': p.payment_method,
                    'status': p.status,
                    'requested_at': p.request_date.isoformat() if p.request_date else None,
                    'processed_at': p.process_date.isoformat() if p.process_date else None,
                    'reseller': {
                        'id': p.reseller.id,
                        'name': p.reseller.company_name or p.reseller.user.get_full_name() or p.reseller.user.username
                    } if p.reseller_id else None
                })

            summary = queryset.aggregate(
                total_amount=Sum('amount'),
                pending_count=Count('id', filter=Q(status=PayoutStatusChoices.REQUESTED)),
                processing_count=Count('id', filter=Q(status=PayoutStatusChoices.PROCESSING)),
                completed_count=Count('id', filter=Q(status=PayoutStatusChoices.COMPLETED)),
                failed_count=Count('id', filter=Q(status=PayoutStatusChoices.FAILED)),
            )

            return {
                'results': results,
                'total_count': paginator.count,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'summary': {
                    'pending_count': summary['pending_count'] or 0,
                    'processing_count': summary['processing_count'] or 0,
                    'completed_count': summary['completed_count'] or 0,
                    'failed_count': summary['failed_count'] or 0,
                    'total_amount': float(summary['total_amount'] or 0)
                }
            }
        except Exception as e:
            raise Exception(f"Error getting payouts list: {str(e)}")

    def get_payout_ids_by_filters(self, filters: Dict[str, Any]) -> List[int]:
        qs = Payout.objects.all()
        if filters.get('status'):
            qs = qs.filter(status=filters['status'])
        if filters.get('reseller_id'):
            qs = qs.filter(reseller_id=filters['reseller_id'])
        return list(qs.values_list('id', flat=True))

    def export_payouts(self, filters: Dict[str, Any], format: str, fields: List[str]) -> Dict[str, Any]:
        import csv, io
        qs = Payout.objects.all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Amount', 'Method', 'Status', 'Requested'])
        for p in qs:
            writer.writerow([p.id, p.amount, p.payment_method, p.status, p.request_date])
        return {'content': output.getvalue(), 'filename': 'payouts.csv', 'record_count': qs.count()}

    def get_payout_detail(self, payout_id: int) -> Dict[str, Any]:
        try:
            p = Payout.objects.select_related('reseller').get(id=payout_id)
            return {
                'id': p.id,
                'amount': float(p.amount),
                'method': p.payment_method,
                'status': p.status,
                'requested_at': p.request_date.isoformat() if p.request_date else None,
                'processed_at': p.process_date.isoformat() if p.process_date else None,
                'completed_at': p.completion_date.isoformat() if p.completion_date else None,
                'reseller': {
                    'id': p.reseller.id,
                    'name': p.reseller.company_name or p.reseller.user.get_full_name() or p.reseller.user.username
                } if p.reseller_id else None
            }
        except Payout.DoesNotExist:
            return {}
        except Exception as e:
            raise Exception(f"Error getting payout detail: {str(e)}")
