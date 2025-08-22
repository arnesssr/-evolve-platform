from typing import Any, Dict, List, Tuple

# NOTE: This service orchestrates admin operations and delegates business logic to domain services
# under App/reseller/... It must not depend on request/response objects.

from App.admin.repositories.resellers_repository import AdminResellersRepository
from App.reseller.earnings.services.reseller_service import ResellerService
from App.reseller.earnings.services.payout_service import PayoutService
from App.reseller.earnings.models.reseller import Reseller
from App.admin.services.audit_service import AuditService
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal


class AdminResellerService:
    def __init__(self) -> None:
        self.repo = AdminResellersRepository()
        self.domain_reseller = ResellerService()

    def list_resellers(self, filters: Dict[str, Any], page: int = 1, page_size: int = 25) -> Tuple[List[Dict[str, Any]], int]:
        """Return a list of resellers and total count based on filters."""
        return self.repo.query_resellers(filters, page=page, page_size=page_size)

    def compute_metrics(self) -> Dict[str, Any]:
        """Compute top-of-page metrics for list view."""
        return self.repo.compute_admin_metrics()

    def get_reseller_detail(self, reseller_id: int) -> Dict[str, Any]:
        """Return a detail view model for a reseller."""
        overview = self.repo.get_reseller_overview(reseller_id)
        commission_summary = self.repo.get_commission_summary(reseller_id)
        sales = self.repo.get_reseller_sales(reseller_id)
        activity = self.repo.get_activity_timeline(reseller_id)
        chart = self.repo.get_chart_series(reseller_id)
        vm: Dict[str, Any] = overview.copy()
        vm.update({
            'pending_commission': commission_summary.get('pending'),
            'monthly_commission': commission_summary.get('monthly_commission'),
            'yearly_commission': commission_summary.get('yearly_commission'),
            'sales': sales,
            'activity': activity,
            'chart_series': chart,
        })
        return vm

    def create_reseller(self, data: Dict[str, Any]) -> int:
        """Create reseller via domain service and return new reseller ID.
        NOTE: This expects a User to exist or to be created outside. For scaffold, we assume
        a user has already been created and provided as part of data (e.g., user_id).
        """
        user_id = data.get('user_id')
        if not user_id:
            # In a real flow, we might create a user here, but admin may want explicit control
            raise ValueError('user_id is required to create a reseller profile')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        profile_data = {
            'company_name': data.get('company'),
            'phone_number': data.get('phone'),
            'paypal_email': data.get('paypal_email'),
            # Map tier/status if applicable; domain tiers are bronze/silver/gold/platinum
        }
        reseller = self.domain_reseller.create_reseller_profile(user, profile_data)
        return reseller.id

    def update_reseller(self, reseller_id: int, data: Dict[str, Any]) -> None:
        """Update reseller via domain service."""
        # Map allowed profile fields into domain update
        profile_data = {
            'company_name': data.get('company'),
            'phone_number': data.get('phone'),
            'company_website': data.get('website'),
            'alternate_email': data.get('email'),
        }
        self.domain_reseller.update_profile(reseller_id, profile_data)

    def suspend_reseller(self, reseller_id: int, reason: str = None, *, actor_id: int | None = None, meta: Dict[str, Any] | None = None) -> None:
        """Suspend reseller via domain service and audit."""
        self.domain_reseller.deactivate_reseller(reseller_id)
        # Audit
        AuditService().log(action='suspend', actor_id=actor_id, target_type='reseller', target_id=reseller_id, details={'reason': reason, **(meta or {})})

    def resume_reseller(self, reseller_id: int, *, actor_id: int | None = None, meta: Dict[str, Any] | None = None) -> None:
        """Resume reseller via domain service and audit."""
        self.domain_reseller.activate_reseller(reseller_id)
        AuditService().log(action='resume', actor_id=actor_id, target_type='reseller', target_id=reseller_id, details=(meta or {}))

    def process_payout(self, reseller_id: int, params: Dict[str, Any]) -> Any:
        """Process payout via domain earnings/payout service.
        Uses PayoutService.request_payout; scheduling info is stored in payment_details for now.
        """
        reseller = Reseller.objects.select_related('user').get(id=reseller_id)
        amount_raw = params.get('amount') or reseller.get_available_balance()
        amount = Decimal(str(amount_raw)) if amount_raw is not None else Decimal('0.00')
        payment_method = params.get('payment_method') or 'bank_transfer'
        details = {
            'schedule': params.get('schedule') or 'immediate',
            'scheduled_date': str(params.get('scheduled_date') or ''),
            'scheduled_time': str(params.get('scheduled_time') or ''),
            'notes': params.get('notes') or '',
        }
        payout_svc = PayoutService()
        payout = payout_svc.request_payout(reseller, amount, payment_method, details)
        AuditService().log(action='payout', actor_id=None, target_type='reseller', target_id=reseller_id, details={'amount': str(amount), 'payment_method': payment_method, **details})
        return payout

    def send_message(self, reseller_ids: List[int], channel: str, payload: Dict[str, Any]) -> None:
        """Send message via email/SMS providers.
        Currently supports email using Django's send_mail; SMS is a TODO.
        reseller_ids may be a list of ints or a comma-separated string.
        """
        if isinstance(reseller_ids, str):
            ids = [int(x) for x in reseller_ids.split(',') if x.strip().isdigit()]
        else:
            ids = reseller_ids or []
        if not ids:
            return
        qs = Reseller.objects.select_related('user').filter(id__in=ids)
        emails = [r.user.email for r in qs if getattr(r.user, 'email', None)]
        subject = payload.get('subject') or 'Message from Platform Admin'
        body = payload.get('body') or ''
        if channel == 'email' and emails and body:
            send_mail(subject, body, getattr(settings, 'EMAIL_HOST_USER', None), emails, fail_silently=True)
        # TODO: implement SMS via provider (e.g., SMSLeopard) when integrated
        AuditService().log(action='message', actor_id=None, target_type='reseller', target_id=','.join(map(str, ids)), details={'channel': channel, 'subject': subject})
        return None

    def export_rows(self, filters: Dict[str, Any]):
        """Yield row dicts for CSV export (use same filters as list)."""
        rows, _ = self.repo.query_resellers(filters, page=1, page_size=10000)
        return rows

    def get_chart_series(self, reseller_id: int) -> Dict[str, Any]:
        return self.repo.get_chart_series(reseller_id)

    def handle_bulk_action(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform bulk action across reseller_ids."""
        action = data.get('action')
        ids_str = data.get('reseller_ids', '')
        ids = [int(x) for x in ids_str.split(',') if x.strip().isdigit()]
        if action == 'suspend':
            for rid in ids:
                self.suspend_reseller(rid)
        elif action == 'resume':
            for rid in ids:
                self.resume_reseller(rid)
        # set_tier and message can be implemented later
        return {'status': 'ok', 'processed': len(ids)}

