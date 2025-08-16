"""Commission service for handling commission logic."""
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import Commission, Reseller
from .base import BaseService


class CommissionService(BaseService):
    """Service class to manage commissions."""

    def create_commission(self, transaction_data):
        """Create a commission record based on transaction data."""
        reseller = transaction_data.get('reseller')
        sale_amount = Decimal(transaction_data.get('sale_amount', 0))
        commission_rate = Decimal(transaction_data.get('commission_rate', 0))
        transaction_reference = transaction_data.get('transaction_reference')

        # Validate required fields
        self.validate_required_fields(transaction_data, ['reseller', 'sale_amount', 'commission_rate', 'transaction_reference'])

        # Positive amount validation
        self.validate_positive_amount(sale_amount, 'sale_amount')
        self.validate_positive_amount(commission_rate, 'commission_rate')

        # Calculate the commission amount
        commission_amount = (sale_amount * commission_rate / 100).quantize(Decimal('0.00'))

        # Create the commission
        commission = Commission.objects.create(
            reseller=reseller,
            transaction_reference=transaction_reference,
            client_name=transaction_data.get('client_name', ''),
            client_email=transaction_data.get('client_email', ''),
            product_name=transaction_data.get('product_name', ''),
            product_type=transaction_data.get('product_type', ''),
            sale_amount=sale_amount,
            amount=commission_amount,
            commission_rate=commission_rate,
            status='pending',
            calculation_date=timezone.now()
        )

        # Update reseller's pending commission
        reseller.pending_commission += commission_amount
        reseller.save(update_fields=['pending_commission'])

        self.log_info(f"Commission created: {commission}")

        return commission

    def approve_commission(self, commission_id):
        """Approve a pending commission."""
        try:
            commission = Commission.objects.get(id=commission_id)
            if commission.status != 'pending':
                raise ValidationError("Commission is not pending.")
            commission.status = 'approved'
            commission.approval_date = timezone.now()
            commission.save(update_fields=['status', 'approval_date'])
            self.log_info(f"Commission approved: {commission}")
            return commission
        except Commission.DoesNotExist:
            raise ValidationError("Commission not found.")

    def pay_commission(self, commission_id):
        """Mark an approved commission as paid."""
        try:
            commission = Commission.objects.get(id=commission_id)
            if commission.status != 'approved':
                raise ValidationError("Commission is not approved.")
            commission.status = 'paid'
            commission.paid_date = timezone.now()
            commission.save(update_fields=['status', 'paid_date'])

            # Update reseller's financial metrics
            reseller = commission.reseller
            reseller.total_commission_earned += commission.amount
            reseller.pending_commission -= commission.amount
            reseller.total_commission_paid += commission.amount
            reseller.save(update_fields=['total_commission_earned', 'pending_commission', 'total_commission_paid'])

            self.log_info(f"Commission paid: {commission}")
            return commission
        except Commission.DoesNotExist:
            raise ValidationError("Commission not found.")
    
    def get_reseller_commissions(self, reseller, filters=None):
        """Get commissions for a specific reseller with optional filters."""
        queryset = Commission.objects.filter(reseller=reseller)
        
        if filters:
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'start_date' in filters:
                queryset = queryset.filter(calculation_date__gte=filters['start_date'])
            if 'end_date' in filters:
                queryset = queryset.filter(calculation_date__lte=filters['end_date'])
        
        return queryset.order_by('-calculation_date')
    
    def get_commission_summary(self, reseller, period='month'):
        """Get commission summary for a reseller."""
        from django.db.models import Sum, Count
        from datetime import datetime, timedelta
        
        now = timezone.now()
        
        if period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        commissions = Commission.objects.filter(
            reseller=reseller,
            calculation_date__gte=start_date
        )
        
        summary = commissions.aggregate(
            total_amount=Sum('amount'),
            total_sales=Sum('sale_amount'),
            count=Count('id')
        )
        
        # Add status breakdown
        status_breakdown = commissions.values('status').annotate(
            count=Count('id'),
            amount=Sum('amount')
        )
        
        return {
            'period': period,
            'start_date': start_date,
            'total_amount': summary['total_amount'] or Decimal('0.00'),
            'total_sales': summary['total_sales'] or Decimal('0.00'),
            'count': summary['count'] or 0,
            'status_breakdown': list(status_breakdown)
        }
    
    def calculate_tier_bonus(self, reseller, base_commission):
        """Calculate tier bonus based on reseller's tier."""
        tier_bonuses = {
            'bronze': Decimal('0.00'),
            'silver': Decimal('0.05'),  # 5% bonus
            'gold': Decimal('0.10'),     # 10% bonus
            'platinum': Decimal('0.15')  # 15% bonus
        }
        
        bonus_rate = tier_bonuses.get(reseller.tier, Decimal('0.00'))
        bonus_amount = (base_commission * bonus_rate).quantize(Decimal('0.00'))
        
        return bonus_amount
    
    def bulk_approve_commissions(self, commission_ids):
        """Approve multiple commissions at once."""
        approved_count = 0
        errors = []
        
        for commission_id in commission_ids:
            try:
                self.approve_commission(commission_id)
                approved_count += 1
            except ValidationError as e:
                errors.append(f"Commission {commission_id}: {str(e)}")
        
        return {
            'approved_count': approved_count,
            'errors': errors
        }
    
    def reject_commission(self, commission_id, reason=''):
        """Reject a pending commission."""
        try:
            commission = Commission.objects.get(id=commission_id)
            if commission.status != 'pending':
                raise ValidationError("Only pending commissions can be rejected.")
            
            commission.status = 'rejected'
            commission.notes = f"Rejected: {reason}" if reason else "Rejected"
            commission.save(update_fields=['status', 'notes'])
            
            # Update reseller's pending commission
            reseller = commission.reseller
            reseller.pending_commission -= commission.amount
            reseller.save(update_fields=['pending_commission'])
            
            self.log_info(f"Commission rejected: {commission}")
            return commission
        except Commission.DoesNotExist:
            raise ValidationError("Commission not found.")

