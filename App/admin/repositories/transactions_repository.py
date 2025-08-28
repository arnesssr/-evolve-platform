"""Admin Transactions Repository - Unified from Invoice, Payout, (optional Commission)"""

from typing import Dict, List, Any
from datetime import datetime
from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

from App.reseller.earnings.models.invoice import Invoice
from App.reseller.earnings.models.payout import Payout
from App.reseller.earnings.models.commission import Commission
from App.reseller.earnings.models.base import InvoiceStatusChoices, PayoutStatusChoices


class TransactionsRepository:
    def _build_unified_queryset(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compose a unified in-memory list of transactions from invoices and payouts."""
        items: List[Dict[str, Any]] = []

        # Invoices => incoming
        inv_qs = Invoice.objects.filter(status=InvoiceStatusChoices.PAID)
        if filters.get('start_date'):
            inv_qs = inv_qs.filter(payment_date__gte=filters['start_date'])
        if filters.get('end_date'):
            inv_qs = inv_qs.filter(payment_date__lte=filters['end_date'])
        if filters.get('min_amount'):
            inv_qs = inv_qs.filter(total_amount__gte=filters['min_amount'])
        if filters.get('max_amount'):
            inv_qs = inv_qs.filter(total_amount__lte=filters['max_amount'])

        for inv in inv_qs.select_related('reseller')[:10000]:
            items.append({
                'id': f'inv-{inv.id}',
                'type': 'incoming',
                'source': 'invoice',
                'amount': float(inv.total_amount),
                'method': 'invoice',
                'status': inv.status,
                'date': inv.payment_date.isoformat() if inv.payment_date else None,
                'counterparty': (inv.reseller.company_name or inv.reseller.user.get_full_name() or inv.reseller.user.username) if inv.reseller_id else None,
            })

        # Payouts => outgoing
        pay_qs = Payout.objects.exclude(status=PayoutStatusChoices.CANCELLED)
        if filters.get('start_date'):
            pay_qs = pay_qs.filter(request_date__gte=filters['start_date'])
        if filters.get('end_date'):
            pay_qs = pay_qs.filter(request_date__lte=filters['end_date'])
        if filters.get('min_amount'):
            pay_qs = pay_qs.filter(amount__gte=filters['min_amount'])
        if filters.get('max_amount'):
            pay_qs = pay_qs.filter(amount__lte=filters['max_amount'])

        for p in pay_qs.select_related('reseller')[:10000]:
            items.append({
                'id': f'pay-{p.id}',
                'type': 'outgoing',
                'source': 'payout',
                'amount': float(p.amount) * -1.0,
                'method': p.payment_method,
                'status': p.status,
                'date': p.completion_date.isoformat() if p.completion_date else (p.process_date.isoformat() if p.process_date else p.request_date.isoformat() if p.request_date else None),
                'counterparty': (p.reseller.company_name or p.reseller.user.get_full_name() or p.reseller.user.username) if p.reseller_id else None,
            })

        # Optional: include approved commissions as internal adjustments (zero effect)
        # Disabled for now to avoid confusion

        # Additional high-level filter by type or status or method
        ttype = filters.get('type')
        if ttype:
            items = [i for i in items if i['type'] == ttype]
        status = filters.get('status')
        if status:
            items = [i for i in items if i['status'] == status]
        method = filters.get('method')
        if method:
            items = [i for i in items if i['method'] == method]

        # Simple search
        if filters.get('search'):
            s = filters['search'].lower()
            items = [i for i in items if (i.get('counterparty') or '').lower().find(s) >= 0 or (i['id']).lower().find(s) >= 0]

        # Sort by date desc
        items.sort(key=lambda x: x['date'] or '', reverse=True)
        return items

    def get_transactions_list(self, page: int, page_size: int, filters: Dict[str, Any]) -> Dict[str, Any]:
        items = self._build_unified_queryset(filters)
        paginator = Paginator(items, page_size)
        page_obj = paginator.get_page(page)

        total_incoming = sum(Decimal(i['amount']) for i in items if i['type'] == 'incoming')
        total_outgoing = sum(Decimal(-i['amount']) for i in items if i['type'] == 'outgoing')
        total_internal = Decimal('0')
        net_amount = total_incoming - total_outgoing

        return {
            'results': list(page_obj.object_list),
            'total_count': paginator.count,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'summary': {
                'total_incoming': float(total_incoming),
                'total_outgoing': float(total_outgoing),
                'total_internal': float(total_internal),
                'net_amount': float(net_amount),
                'transaction_count': paginator.count,
            }
        }

    def get_volume_by_interval(self, start_date: datetime, end_date: datetime, interval: str) -> List[Dict[str, Any]]:
        if interval == 'daily':
            trunc_inv = TruncDay('payment_date')
            trunc_pay = TruncDay('completion_date')
        elif interval == 'weekly':
            trunc_inv = TruncWeek('payment_date')
            trunc_pay = TruncWeek('completion_date')
        else:
            trunc_inv = TruncMonth('payment_date')
            trunc_pay = TruncMonth('completion_date')

        inv = (Invoice.objects.filter(status=InvoiceStatusChoices.PAID, payment_date__range=[start_date, end_date])
               .annotate(period=trunc_inv)
               .values('period')
               .annotate(amount=Sum('total_amount'))
               .order_by('period'))
        pay = (Payout.objects.filter(status=PayoutStatusChoices.COMPLETED, completion_date__range=[start_date, end_date])
               .annotate(period=trunc_pay)
               .values('period')
               .annotate(amount=Sum('amount'))
               .order_by('period'))

        from collections import defaultdict
        periods = defaultdict(lambda: {'incoming': Decimal('0'), 'outgoing': Decimal('0'), 'internal': Decimal('0')})
        for row in inv:
            key = row['period'].strftime('%Y-%m-%d') if interval == 'daily' else row['period'].strftime('%Y-%m')
            periods[key]['incoming'] += Decimal(row['amount'] or 0)
        for row in pay:
            key = row['period'].strftime('%Y-%m-%d') if interval == 'daily' else row['period'].strftime('%Y-%m')
            periods[key]['outgoing'] += Decimal(row['amount'] or 0)

        return [
            {
                'period': k,
                'incoming': float(v['incoming']),
                'outgoing': float(v['outgoing']),
                'internal': float(v['internal']),
            }
            for k, v in sorted(periods.items())
        ]

    def get_type_breakdown(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        incoming = Invoice.objects.filter(status=InvoiceStatusChoices.PAID, payment_date__range=[start_date, end_date]).aggregate(s=Sum('total_amount'))['s'] or 0
        outgoing = Payout.objects.filter(status=PayoutStatusChoices.COMPLETED, completion_date__range=[start_date, end_date]).aggregate(s=Sum('amount'))['s'] or 0
        return {'incoming': float(incoming), 'outgoing': float(outgoing), 'internal': 0.0}

    def get_method_breakdown(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        # For now, only payout methods
        from django.db.models import F
        data = Payout.objects.filter(completion_date__range=[start_date, end_date]).values('payment_method').annotate(s=Sum('amount'))
        return {row['payment_method']: float(row['s'] or 0) for row in data}

    def get_transaction_count(self, start_date: datetime, end_date: datetime) -> int:
        inv = Invoice.objects.filter(status=InvoiceStatusChoices.PAID, payment_date__range=[start_date, end_date]).count()
        pay = Payout.objects.filter(completion_date__range=[start_date, end_date]).count()
        return inv + pay

    def mark_transaction_reconciled(self, transaction_id: int, reconciliation_date: str, reference: str, notes: str, user) -> bool:
        # Not implemented for demo; would set flags on source objects
        return True

    def mark_transaction_disputed(self, transaction_id: int, reason: str, user) -> bool:
        # Not implemented for demo
        return True

    def auto_reconcile_transactions(self, start_date: str, end_date: str, tolerance: float, user) -> Dict[str, Any]:
        return {'processed_count': 0, 'failed_count': 0}

    def export_transactions(self, filters: Dict[str, Any], format: str, fields: List[str], include_summary: bool) -> Dict[str, Any]:
        import csv, io
        items = self._build_unified_queryset(filters)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Type', 'Amount', 'Method', 'Status', 'Date', 'Counterparty'])
        for i in items:
            writer.writerow([i['id'], i['type'], i['amount'], i['method'], i['status'], i['date'], i['counterparty']])
        return {'content': output.getvalue(), 'filename': 'transactions.csv', 'record_count': len(items)}

    def get_transaction_detail(self, transaction_id: int, include_related: bool) -> Dict[str, Any]:
        # transaction_id format: inv-<id> or pay-<id>
        try:
            sid, raw_id = str(transaction_id).split('-') if isinstance(transaction_id, str) and '-' in str(transaction_id) else (None, None)
        except ValueError:
            sid, raw_id = None, None
        # Not fully implemented; return empty
        return {}

    def get_cash_flow_by_interval(self, start_date: datetime, end_date: datetime, interval: str) -> List[Dict[str, Any]]:
        data = self.get_volume_by_interval(start_date, end_date, interval)
        return [
            {
                'period': d['period'],
                'inflow': d['incoming'],
                'outflow': d['outgoing'],
            }
            for d in data
        ]

    def get_reconciliation_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        return {}

    def get_transaction_summary(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        items = self._build_unified_queryset(filters)
        total_incoming = sum(Decimal(i['amount']) for i in items if i['type'] == 'incoming')
        total_outgoing = sum(Decimal(-i['amount']) for i in items if i['type'] == 'outgoing')
        net_amount = total_incoming - total_outgoing
        return {
            'total_incoming': float(total_incoming),
            'total_outgoing': float(total_outgoing),
            'net_amount': float(net_amount),
            'transaction_count': len(items),
        }
