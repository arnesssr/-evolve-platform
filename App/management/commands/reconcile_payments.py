from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from App.models import PaymentRecord, Plan, Subscription
from App.integrations import pesapal_service

class Command(BaseCommand):
    help = "Reconcile pending PaymentRecords by querying Pesapal status and updating them (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=200, help="Max records to process")

    def handle(self, *args, **opts):
        limit = opts.get("limit") or 200
        token = pesapal_service.generate_access_token()
        if not token:
            self.stderr.write(self.style.ERROR("Failed to obtain Pesapal access token"))
            return 1

        qs = PaymentRecord.objects.filter(status='initiated').order_by('created_at')[:limit]
        processed = 0
        completed = 0
        failed = 0
        skipped = 0

        for pr in qs:
            processed += 1
            # We need at least the merchant reference; tracking id is optional
            merchant_ref = pr.order_id
            tracking_id = pr.provider_tracking_id or None

            try:
                details = pesapal_service.get_transaction_status_details(token, tracking_id, merchant_ref)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"[{merchant_ref}] status fetch failed: {e}"))
                skipped += 1
                continue

            status = (details.get('status') or '').upper()
            if status not in ('COMPLETED', 'FAILED'):
                # Still pending or unknown; skip for now
                skipped += 1
                continue

            # Update PR fields
            pr.provider_status = status
            if details.get('tracking_id') and not pr.provider_tracking_id:
                pr.provider_tracking_id = details.get('tracking_id')
            if details.get('phone_number'):
                pr.phone_number = (details.get('phone_number') or '')[:20]
            if details.get('payment_method'):
                pr.payment_method = (details.get('payment_method') or '')[:50]
            pr.status = 'completed' if status == 'COMPLETED' else 'failed'
            pr.save(update_fields=['provider_status', 'provider_tracking_id', 'phone_number', 'payment_method', 'status', 'updated_at'])

            if status == 'COMPLETED':
                completed += 1
                # Ensure subscription exists/updated (mirror logic from views)
                billing = (pr.billing or 'monthly')
                plan = Plan.objects.filter(is_active=True).order_by('display_order').first()
                # Optionally infer plan by name saved earlier
                if pr.plan_name:
                    p2 = Plan.objects.filter(name=pr.plan_name).first()
                    if p2:
                        plan = p2
                if plan:
                    now = timezone.now()
                    period_days = 365 if billing == 'yearly' else 30
                    Subscription.objects.update_or_create(
                        user=pr.user,
                        product='payroll',
                        defaults={
                            'plan': plan,
                            'status': 'active',
                            'start_date': now,
                            'end_date': now + timezone.timedelta(days=period_days),
                            'auto_renewal': True,
                        }
                    )
                # Commission idempotency (optional): create if AFF= present and no existing record
                try:
                    desc = pr.description or ''
                    if 'AFF=' in desc:
                        from App.reseller.marketing.models import MarketingLink as ML
                        from App.reseller.earnings.models.reseller import Reseller as ResellerModel
                        from App.reseller.earnings.models import Commission as CommissionModel
                        from App.reseller.earnings.services.commission_service import CommissionService
                        aff = desc.split('AFF=', 1)[1].strip()
                        ml = ML.objects.filter(code=aff, is_active=True).first()
                        tx_ref = pr.provider_tracking_id or pr.order_id
                        if ml and not CommissionModel.objects.filter(transaction_reference=tx_ref).exists():
                            reseller = ResellerModel.objects.get(id=ml.reseller_id)
                            sale_amount = float(pr.amount)
                            commission_rate = float(reseller.get_tier_commission_rate())
                            client_name = (pr.user.get_full_name() or pr.user.username)
                            client_email = pr.user.email
                            notes = f"link_code={aff}; product=payroll; billing={billing}"
                            CommissionService().create_commission({
                                'reseller': reseller,
                                'sale_amount': sale_amount,
                                'commission_rate': commission_rate,
                                'transaction_reference': tx_ref,
                                'client_name': client_name,
                                'client_email': client_email,
                                'product_name': 'Payroll Subscription',
                                'product_type': 'subscription',
                                'notes': notes,
                            })
                except Exception as ce:
                    self.stderr.write(self.style.WARNING(f"[{merchant_ref}] commission creation skipped: {ce}"))
            else:
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f"Reconcile done. processed={processed} completed={completed} failed={failed} skipped={skipped}"
        ))

