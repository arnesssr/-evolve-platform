"""
Admin Revenue Repository
Handles data access for revenue metrics, trends, and analytics.
"""

from datetime import datetime
from typing import Dict, List, Any
from decimal import Decimal

from django.db.models import Sum, Count, Avg, Q, Value, DecimalField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, Coalesce

from App.reseller.earnings.models.invoice import Invoice
from App.reseller.earnings.models.commission import Commission
from App.reseller.earnings.models.payout import Payout
from App.reseller.earnings.models.reseller import Reseller
from App.reseller.earnings.models.base import InvoiceStatusChoices, PayoutStatusChoices


class RevenueRepository:
    """Repository for revenue-related data access"""

    def get_revenue_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get basic revenue metrics from invoices, commissions, and payouts"""
        try:
            revenue_qs = Invoice.objects.filter(
                status=InvoiceStatusChoices.PAID,
                payment_date__range=[start_date, end_date],
            )
            revenue_data = revenue_qs.aggregate(
                total_revenue=Coalesce(Sum('total_amount'), Value(0), output_field=DecimalField()),
                invoice_count=Coalesce(Count('id'), Value(0)),
                avg_invoice_value=Coalesce(Avg('total_amount'), Value(0), output_field=DecimalField()),
            )

            commission_qs = Commission.objects.filter(
                created_at__range=[start_date, end_date]
            )
            commission_data = commission_qs.aggregate(
                pending_commissions=Coalesce(Sum('amount', filter=Q(status='pending')), Value(0), output_field=DecimalField()),
                avg_commission_rate=Coalesce(Avg('commission_rate'), Value(0), output_field=DecimalField()),
            )

            payout_qs = Payout.objects.filter(
                status=PayoutStatusChoices.COMPLETED,
                completion_date__range=[start_date, end_date]
            )
            payout_data = payout_qs.aggregate(
                processed_payouts=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
            )

            return {
                'total_revenue': Decimal(revenue_data['total_revenue']),
                'invoice_count': int(revenue_data['invoice_count']),
                'avg_invoice_value': Decimal(revenue_data['avg_invoice_value']),
                'pending_commissions': Decimal(commission_data['pending_commissions']),
                'avg_commission_rate': Decimal(commission_data['avg_commission_rate']),
                'processed_payouts': Decimal(payout_data['processed_payouts'])
            }
        except Exception as e:
            raise Exception(f"Error getting revenue metrics: {str(e)}")

    def get_revenue_by_source(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get revenue breakdown by source (resellers)"""
        try:
            qs = (
                Invoice.objects.filter(
                    status=InvoiceStatusChoices.PAID,
                    payment_date__range=[start_date, end_date]
                )
                .values('reseller_id')
                .annotate(
                    total_amount=Coalesce(Sum('total_amount'), Value(0), output_field=DecimalField()),
                    invoice_count=Count('id')
                )
                .order_by('-total_amount')
            )

            results: List[Dict[str, Any]] = []
            reseller_map = {r.id: r for r in Reseller.objects.filter(id__in=[row['reseller_id'] for row in qs])}
            for row in qs:
                reseller = reseller_map.get(row['reseller_id'])
                name = (reseller.company_name or reseller.user.get_full_name() or reseller.user.username) if reseller else 'Unknown'
                results.append({
                    'name': name,
                    'id': row['reseller_id'],
                    'amount': Decimal(row['total_amount']),
                    'invoice_count': row['invoice_count']
                })
            return results
        except Exception as e:
            raise Exception(f"Error getting revenue by source: {str(e)}")

    def get_revenue_trends(self, start_date: datetime, end_date: datetime, interval: str = 'monthly') -> List[Dict[str, Any]]:
        """Get revenue trends over time"""
        try:
            if interval == 'daily':
                trunc = TruncDay('payment_date')
            elif interval == 'weekly':
                trunc = TruncWeek('payment_date')
            else:
                trunc = TruncMonth('payment_date')

            invoice_trends = (
                Invoice.objects.filter(
                    status=InvoiceStatusChoices.PAID,
                    payment_date__range=[start_date, end_date]
                )
                .annotate(period=trunc)
                .values('period')
                .annotate(revenue=Coalesce(Sum('total_amount'), Value(0), output_field=DecimalField()))
                .order_by('period')
            )

            # For commissions, use paid_date if available; fallback to created_at
            if interval == 'daily':
                c_trunc = TruncDay('paid_date')
            elif interval == 'weekly':
                c_trunc = TruncWeek('paid_date')
            else:
                c_trunc = TruncMonth('paid_date')

            commission_trends = (
                Commission.objects.filter(
                    paid_date__isnull=False,
                    paid_date__range=[start_date, end_date]
                )
                .annotate(period=c_trunc)
                .values('period')
                .annotate(commissions=Coalesce(Sum('amount'), Value(0), output_field=DecimalField()))
                .order_by('period')
            )

            # Merge periods
            from collections import defaultdict
            merged = defaultdict(lambda: {'revenue': Decimal('0'), 'commissions': Decimal('0')})
            for row in invoice_trends:
                key = row['period'].strftime('%Y-%m-%d') if interval == 'daily' else row['period'].strftime('%Y-%m')
                merged[key]['revenue'] = Decimal(row['revenue'])
            for row in commission_trends:
                key = row['period'].strftime('%Y-%m-%d') if interval == 'daily' else row['period'].strftime('%Y-%m')
                merged[key]['commissions'] = Decimal(row['commissions'])

            periods_sorted = sorted(merged.keys())
            return [
                {
                    'period': p,
                    'revenue': merged[p]['revenue'],
                    'commissions': merged[p]['commissions']
                }
                for p in periods_sorted
            ]
        except Exception as e:
            raise Exception(f"Error getting revenue trends: {str(e)}")

    def get_top_revenue_sources(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top revenue sources (resellers)"""
        try:
            qs = (
                Invoice.objects.filter(
                    status=InvoiceStatusChoices.PAID,
                    payment_date__range=[start_date, end_date]
                )
                .values('reseller_id')
                .annotate(
                    total_revenue=Coalesce(Sum('total_amount'), Value(0), output_field=DecimalField()),
                    invoice_count=Count('id'),
                    avg_invoice_value=Coalesce(Avg('total_amount'), Value(0), output_field=DecimalField())
                )
                .order_by('-total_revenue')[:limit]
            )

            reseller_map = {r.id: r for r in Reseller.objects.filter(id__in=[row['reseller_id'] for row in qs])}
            results: List[Dict[str, Any]] = []
            for row in qs:
                reseller = reseller_map.get(row['reseller_id'])
                name = (reseller.company_name or reseller.user.get_full_name() or reseller.user.username) if reseller else 'Unknown'
                results.append({
                    'name': name,
                    'id': row['reseller_id'],
                    'company': reseller.company_name if reseller else '',
                    'revenue': Decimal(row['total_revenue']),
                    'invoice_count': row['invoice_count'],
                    'avg_invoice_value': Decimal(row['avg_invoice_value'])
                })
            return results
        except Exception as e:
            raise Exception(f"Error getting top revenue sources: {str(e)}")
