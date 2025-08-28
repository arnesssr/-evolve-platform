from typing import Any, Dict, List, Tuple

# NOTE: This service orchestrates admin operations and delegates business logic to domain services
# under App/reseller/... It must not depend on request/response objects.

from App.admin.repositories.resellers_repository import AdminResellersRepository
from App.reseller.earnings.services.reseller_service import ResellerService
from App.reseller.earnings.services import PayoutService
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
        If user_id is not provided, create a new user from first_name/last_name/email.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_id = data.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            email = data.get('email')
            if not email:
                raise ValueError('email is required to create a new user')
            first_name = data.get('first_name') or ''
            last_name = data.get('last_name') or ''
            base_username = (email.split('@')[0] or 'user').lower()
            username = base_username
            suffix = 1
            while User.objects.filter(**({'username': username} if hasattr(User, 'USERNAME_FIELD') and User.USERNAME_FIELD == 'username' else {'email': email})).exists():
                username = f"{base_username}{suffix}"
                suffix += 1
            # Create user: for default Django, username is required; use email as username
            if hasattr(User, 'USERNAME_FIELD') and User.USERNAME_FIELD == 'email':
                user = User.objects.create_user(email=email, password=None)
            else:
                user = User.objects.create_user(username=username, email=email, password=None)
            # Mark password unusable to force set/reset flow later
            try:
                user.set_unusable_password()
                user.save(update_fields=['password'])
            except Exception:
                pass
            # Set names
            try:
                user.first_name = first_name
                user.last_name = last_name
                user.save(update_fields=['first_name', 'last_name'])
            except Exception:
                pass
        # Sanitize optional strings to avoid NULLs for non-nullable columns
        company = (data.get('company') or '').strip()
        phone = (data.get('phone') or '').strip()
        paypal_email = (data.get('paypal_email') or '').strip()
        profile_data = {
            'company_name': company,
            'phone_number': phone,
            'paypal_email': paypal_email,
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
        processed = 0

        if action == 'suspend':
            for rid in ids:
                self.suspend_reseller(rid)
                processed += 1
        elif action == 'resume':
            for rid in ids:
                self.resume_reseller(rid)
                processed += 1
        elif action == 'delete':
            # Soft delete: deactivate reseller accounts
            from App.reseller.earnings.models import Reseller
            for rid in ids:
                Reseller.objects.filter(id=rid).update(is_active=False)
                processed += 1
        elif action == 'set_tier':
            # Map UI tiers to domain tiers
            tier = (data.get('tier') or '').lower()
            tier_map = {
                'basic': 'bronze',
                'standard': 'silver',
                'premium': 'gold',
                'platinum': 'platinum',
            }
            domain_tier = tier_map.get(tier)
            if domain_tier:
                for rid in ids:
                    # Update profile tier via domain service
                    self.domain_reseller.update_profile(rid, {'tier': domain_tier})
                    processed += 1
        elif action == 'message':
            # Send notification via email only for now
            payload = {
                'subject': data.get('subject') or 'Message from Platform Admin',
                'body': data.get('message') or '',
            }
            if payload['body']:
                self.send_message(ids, 'email', payload)
                processed = len(ids)
        else:
            # Unknown or unsupported action
            return {'status': 'error', 'error': f'Unsupported action: {action}', 'processed': 0}

        return {'status': 'ok', 'processed': processed}

