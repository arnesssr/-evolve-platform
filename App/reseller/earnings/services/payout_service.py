"""Payout service for handling payouts logic."""
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import Payout, Reseller, Invoice, Commission
from .base import BaseService


class PayoutService(BaseService):
    """Service class to manage payouts."""

    def request_payout(self, reseller, amount, payment_method, details):
        """Request a new payout for a reseller."""
        self.validate_positive_amount(amount, 'amount')

        # Validate reseller balance
        available_balance = reseller.get_available_balance()
        if amount > available_balance:
            raise ValidationError("Requested amount exceeds available balance.")

        # Create payout
        payout = Payout.objects.create(
            reseller=reseller,
            amount=amount,
            payment_method=payment_method,
            payment_details=details,
            status='requested'
        )

        # Update reseller's pending commission
        reseller.pending_commission -= amount
        reseller.save(update_fields=['pending_commission'])

        self.log_info(f"Payout requested: {payout}")
        return payout

    def process_payout(self, payout_id):
        """Process payout request."""
        try:
            payout = Payout.objects.get(id=payout_id)
            if payout.status != 'requested':
                raise ValidationError("Only requested payouts can be processed.")

            payout.process_payout()
            self.log_info(f"Payout processing: {payout}")
            return payout
        except Payout.DoesNotExist:
            raise ValidationError("Payout not found.")

    def complete_payout(self, payout_id, transaction_reference):
        """Complete a payout."""
        try:
            payout = Payout.objects.get(id=payout_id)
            if payout.status != 'processing':
                raise ValidationError("Only processing payouts can be completed.")

            payout.complete_payout(transaction_reference)
            self.log_info(f"Payout completed: {payout}")
            return payout
        except Payout.DoesNotExist:
            raise ValidationError("Payout not found.")

    def fail_payout(self, payout_id, reason=''):
        """Fail a payout."""
        try:
            payout = Payout.objects.get(id=payout_id)
            if payout.status not in ['requested', 'processing']:
                raise ValidationError("Only requested or processing payouts can be failed.")

            payout.fail_payout(reason)

            # Refund to reseller's pending commission
            reseller = payout.reseller
            reseller.pending_commission += payout.amount
            reseller.save(update_fields=['pending_commission'])

            self.log_info(f"Payout failed: {payout}")
            return payout
        except Payout.DoesNotExist:
            raise ValidationError("Payout not found.")

    def get_reseller_payouts(self, reseller, filters=None):
        """Get payouts for a specific reseller with optional filters."""
        queryset = Payout.objects.filter(reseller=reseller)

        if filters:
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'start_date' in filters:
                queryset = queryset.filter(request_date__gte=filters['start_date'])
            if 'end_date' in filters:
                queryset = queryset.filter(request_date__lte=filters['end_date'])

        return queryset.order_by('-request_date')

    def get_payout_history(self, reseller):
        """Get complete payout history for a reseller."""
        return Payout.objects.filter(reseller=reseller).order_by('-request_date')
    
    def get_payout_summary(self, reseller):
        """Get payout summary for a reseller."""
        from django.db.models import Sum, Count
        
        payouts = Payout.objects.filter(reseller=reseller)
        
        summary = {
            'total_paid': payouts.filter(status='completed').aggregate(
                Sum('amount'))['amount__sum'] or Decimal('0.00'),
            'available_balance': reseller.get_available_balance(),
            'pending_amount': payouts.filter(
                status__in=['requested', 'processing']
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
            'total_payouts': payouts.count(),
            'completed_payouts': payouts.filter(status='completed').count(),
            'failed_payouts': payouts.filter(status='failed').count(),
        }
        
        # Get next payout date (example: 15th of next month)
        today = timezone.now().date()
        if today.day <= 15:
            summary['next_payout_date'] = today.replace(day=15)
        else:
            next_month = today.month + 1 if today.month < 12 else 1
            next_year = today.year if today.month < 12 else today.year + 1
            summary['next_payout_date'] = today.replace(year=next_year, month=next_month, day=15)
        
        return summary
    
    def validate_payout_request(self, reseller, amount):
        """Validate if a payout request can be made."""
        # Check minimum payout amount
        MIN_PAYOUT_AMOUNT = Decimal('50.00')
        if amount < MIN_PAYOUT_AMOUNT:
            raise ValidationError(f"Minimum payout amount is ${MIN_PAYOUT_AMOUNT}")
        
        # Check if reseller has pending payouts
        pending_payouts = Payout.objects.filter(
            reseller=reseller,
            status__in=['requested', 'processing']
        ).exists()
        
        if pending_payouts:
            raise ValidationError("You have pending payouts. Please wait for them to complete.")
        
        # Check available balance
        available_balance = reseller.get_available_balance()
        if amount > available_balance:
            raise ValidationError(f"Insufficient balance. Available: ${available_balance}")
        
        return True
    
    def calculate_payout_fee(self, amount, payment_method):
        """Calculate payout processing fee."""
        fee_structure = {
            'bank_transfer': {'fixed': Decimal('5.00'), 'percentage': Decimal('0.00')},
            'paypal': {'fixed': Decimal('0.00'), 'percentage': Decimal('2.90')},
            'stripe': {'fixed': Decimal('0.00'), 'percentage': Decimal('2.90')},
            'check': {'fixed': Decimal('10.00'), 'percentage': Decimal('0.00')},
            'other': {'fixed': Decimal('5.00'), 'percentage': Decimal('0.00')},
        }
        
        fees = fee_structure.get(payment_method, fee_structure['other'])
        fixed_fee = fees['fixed']
        percentage_fee = (amount * fees['percentage'] / 100).quantize(Decimal('0.01'))
        
        return fixed_fee + percentage_fee
    
    def bulk_process_payouts(self, payout_ids):
        """Process multiple payouts at once."""
        processed_count = 0
        errors = []
        
        for payout_id in payout_ids:
            try:
                self.process_payout(payout_id)
                processed_count += 1
            except ValidationError as e:
                errors.append(f"Payout {payout_id}: {str(e)}")
        
        return {
            'processed_count': processed_count,
            'errors': errors
        }
    
    def get_payout_requests(self):
        """Get all pending payout requests."""
        return Payout.objects.filter(status='requested').select_related('reseller__user')
