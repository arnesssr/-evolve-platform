# Read-optimized queries and aggregates for admin reseller pages
from typing import Any, Dict, List, Tuple
from datetime import datetime

from django.db.models import Count, Sum, Q, F
from django.utils import timezone

from App.reseller.earnings.models.reseller import Reseller
from App.reseller.earnings.models.commission import Commission


class AdminResellersRepository:
    def _map_commission_tier_filter(self, tier: str):
        """Map admin filter values to domain tier choices.
        Admin filters use: basic|standard|premium
        Domain tiers: bronze|silver|gold|platinum
        """
        tier = (tier or '').lower()
        if tier == 'basic':
            return ['bronze']
        if tier == 'standard':
            return ['silver']
        if tier == 'premium':
            return ['gold', 'platinum']
        return []

    def _map_status_filter(self, status: str):
        """Map admin status to field filters."""
        status = (status or '').lower()
        if status == 'active':
            return {'is_active': True}
        if status == 'suspended':
            return {'is_active': False}
        if status == 'pending':
            # Treat pending as not verified
            return {'is_verified': False}
        return {}

    def _map_performance_filter(self, performance: str):
        """Return Q filter for performance bands based on total_sales thresholds.
        Excellent/top: >= 50000
        Good: >= 15000 and < 50000
        Average: >= 5000 and < 15000
        Poor: < 5000
        """
        performance = (performance or '').lower()
        if performance in ('top', 'excellent'):
            return Q(total_sales__gte=50000)
        if performance in ('good',):
            return Q(total_sales__gte=15000, total_sales__lt=50000)
        if performance in ('average',):
            return Q(total_sales__gte=5000, total_sales__lt=15000)
        if performance in ('poor', 'needs improvement'):
            return Q(total_sales__lt=5000)
        return Q()

    def _performance_segment_and_score(self, total_sales):
        """Derive human segment label and a 0-100 score for UI bars."""
        try:
            val = float(total_sales or 0)
        except Exception:
            val = 0.0
        if val >= 50000:
            return 'Excellent', 95
        if val >= 15000:
            return 'Good', 78
        if val >= 5000:
            return 'Average', 55
        return 'Needs Improvement', 25

    def _commission_tier_label(self, tier: str, commission_rate):
        tier = (tier or '').lower()
        rate = commission_rate or 0
        if tier == 'bronze':
            return f"Basic ({rate}%)"
        if tier == 'silver':
            return f"Standard ({rate}%)"
        if tier == 'gold':
            return f"Premium ({rate}%)"
        if tier == 'platinum':
            return f"Premium+ ({rate}%)"
        return f"Tier ({rate}%)"

    def query_resellers(self, filters: Dict[str, Any], order: str = '-joined_at', page: int = 1, page_size: int = 25) -> Tuple[List[Dict[str, Any]], int]:
        qs = Reseller.objects.select_related('user').all()

        # Text search (q)
        q_text = (filters.get('q') or '').strip()
        if q_text:
            qs = qs.filter(
                Q(user__username__icontains=q_text)
                | Q(user__email__icontains=q_text)
                | Q(user__first_name__icontains=q_text)
                | Q(user__last_name__icontains=q_text)
                | Q(company_name__icontains=q_text)
                | Q(referral_code__icontains=q_text)
            )

        # Commission tier filter
        tier_val = filters.get('commission_tier')
        mapped_tiers = self._map_commission_tier_filter(tier_val)
        if mapped_tiers:
            qs = qs.filter(tier__in=mapped_tiers)

        # Status filter
        status_filters = self._map_status_filter(filters.get('status'))
        if status_filters:
            qs = qs.filter(**status_filters)

        # Performance filter
        perf_q = self._map_performance_filter(filters.get('performance'))
        if perf_q:
            qs = qs.filter(perf_q)

        # Date range filters (joined_from/joined_to)
        joined_from = filters.get('joined_from')
        joined_to = filters.get('joined_to')
        if joined_from:
            qs = qs.filter(joined_at__date__gte=joined_from)
        if joined_to:
            qs = qs.filter(joined_at__date__lte=joined_to)

        # Annotations for counts
        start_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        qs = qs.annotate(
            total_earnings=F('total_commission_earned'),
            sales_count=Count('commissions', distinct=True),
            monthly_sales_count=Count('commissions', filter=Q(commissions__calculation_date__gte=start_month), distinct=True),
        )

        total = qs.count()

        # Ordering
        order_by = order or '-joined_at'
        qs = qs.order_by(order_by)

        # Pagination
        offset = max(0, (int(page or 1) - 1) * int(page_size or 25))
        limit = offset + int(page_size or 25)
        page_qs = list(qs[offset:limit])

        rows: List[Dict[str, Any]] = []
        for r in page_qs:
            perf_label, perf_score = self._performance_segment_and_score(r.total_sales)
            # derive name and email
            user = r.user
            full_name = (user.get_full_name() or '').strip()
            name = full_name or user.username
            email = user.email
            rows.append({
                'id': r.id,
                'name': name,
                'email': email,
                'company': r.company_name or '',
                'performance_segment': perf_label,
                'performance_score': perf_score,
                'commission_tier': self._commission_tier_label(r.tier, r.commission_rate),
                'total_earnings': float(r.total_earnings or 0),
                'sales_count': r.sales_count or 0,
                'sales_this_month': r.monthly_sales_count or 0,
                'status': 'active' if r.is_active else 'suspended',
                'joined': r.joined_at,
            })

        return rows, total

    def compute_admin_metrics(self) -> Dict[str, Any]:
        agg = Reseller.objects.aggregate(
            total_resellers=Count('id'),
            active_resellers=Count('id', filter=Q(is_active=True)),
            total_commission=Sum('total_commission_earned'),
        )
        top = (
            Reseller.objects.select_related('user')
            .filter(is_active=True)
            .order_by('-total_sales')
            .first()
        )
        top_name = None
        if top:
            full_name = (top.user.get_full_name() or '').strip()
            top_name = full_name or top.user.username
        return {
            'total_resellers': agg.get('total_resellers') or 0,
            'active_resellers': agg.get('active_resellers') or 0,
            'total_commission': float(agg.get('total_commission') or 0),
            'top_performer': top_name,
        }

    def get_reseller_overview(self, reseller_id: int) -> Dict[str, Any]:
        r = Reseller.objects.select_related('user').get(id=reseller_id)
        perf_label, perf_score = self._performance_segment_and_score(r.total_sales)

        def _mask(val: str) -> str:
            if not val:
                return ''
            s = str(val)
            return ('****' + s[-4:]) if len(s) >= 4 else '****'

        return {
            'id': r.id,
            'name': (r.user.get_full_name() or r.user.username),
            'email': r.user.email,
            'phone': r.phone_number,
            'company': r.company_name,
            'specialization': '',  # domain not defined; placeholder
            'territory': '',  # placeholder
            'website': r.company_website,
            'status': 'active' if r.is_active else 'suspended',
            'tier': r.tier,
            'commission_rate': float(r.commission_rate or 0),
            'referral_code': r.referral_code,
            'join_date': r.joined_at,
            'last_login': r.user.last_login,
            'performance_segment': perf_label,
            'performance_score': perf_score,
            'total_earnings': float(r.total_commission_earned or 0),
            # Payout-related fields
            'available_balance': float(r.get_available_balance() or 0),
            'payment_method': r.payment_method or '',
            'paypal_email': r.paypal_email or '',
            'bank_name': r.bank_name or '',
            'bank_account_name': r.bank_account_name or '',
            'bank_account_number_masked': _mask(r.bank_account_number),
            'bank_routing_number_masked': _mask(r.bank_routing_number),
            'address': r.address or '',
            'city': r.city or '',
            'state': r.state or '',
            'country': r.country or '',
            'postal_code': r.postal_code or '',
        }

    def get_commission_summary(self, reseller_id: int) -> Dict[str, Any]:
        # Pending directly from reseller, monthly/yearly via Commission aggregation
        reseller = Reseller.objects.get(id=reseller_id)
        now = timezone.now()
        start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        month_sum = Commission.objects.filter(reseller_id=reseller_id, calculation_date__gte=start_month).aggregate(sum=Sum('amount')).get('sum') or 0
        year_sum = Commission.objects.filter(reseller_id=reseller_id, calculation_date__gte=start_year).aggregate(sum=Sum('amount')).get('sum') or 0
        return {
            'pending': float(reseller.pending_commission or 0),
            'monthly_commission': float(month_sum),
            'yearly_commission': float(year_sum),
        }

    def get_reseller_sales(self, reseller_id: int, months: int = 1) -> List[Dict[str, Any]]:
        # Example: last N entries (most recent commissions)
        qs = (
            Commission.objects.filter(reseller_id=reseller_id)
            .order_by('-calculation_date')[:20]
            .values('client_name', 'product_name', 'sale_amount', 'amount', 'calculation_date', 'status')
        )
        rows: List[Dict[str, Any]] = []
        for c in qs:
            rows.append({
                'business': c['client_name'],
                'plan': c['product_name'],
                'sale_amount': float(c['sale_amount'] or 0),
                'commission': float(c['amount'] or 0),
                'date': c['calculation_date'],
                'status': c['status'],
            })
        return rows

    def get_activity_timeline(self, reseller_id: int) -> List[Dict[str, Any]]:
        # Placeholder: In absence of audit model, synthesize recent items from commissions
        qs = Commission.objects.filter(reseller_id=reseller_id).order_by('-calculation_date')[:5]
        items: List[Dict[str, Any]] = []
        for c in qs:
            items.append({
                'ts': c.calculation_date,
                'type': 'commission',
                'text': f"Commission {c.amount} for {c.product_name}",
            })
        return items

    def get_chart_series(self, reseller_id: int, months: int = 12) -> Dict[str, Any]:
        # Aggregate monthly commission counts for chart
        from django.db.models.functions import TruncMonth
        now = timezone.now()
        start = (now.replace(day=1) - timezone.timedelta(days=months*31)).replace(day=1)
        qs = (
            Commission.objects.filter(reseller_id=reseller_id, calculation_date__gte=start)
            .annotate(month=TruncMonth('calculation_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        labels = [x['month'].strftime('%b %Y') for x in qs if x['month']]
        values = [x['count'] for x in qs]
        return {'labels': labels, 'values': values}

