"""API views for reseller operations."""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from ..forms import PayoutRequestForm, InvoiceRequestForm
from ..services import CommissionService, InvoiceService, PayoutService

@login_required
@require_POST
def request_payout(request):
    """Handle payout requests."""
    form = PayoutRequestForm(request.POST)
    if form.is_valid():
        payout_service = PayoutService()
        try:
            payout = payout_service.request_payout(
                reseller=request.user.reseller_profile,
                amount=form.cleaned_data['amount'],
                payment_method=form.cleaned_data['payment_method'],
                details={
                    'bank_account_number': form.cleaned_data.get('bank_account_number'),
                    'bank_routing_number': form.cleaned_data.get('bank_routing_number'),
                    'paypal_email': form.cleaned_data.get('paypal_email')
                }
            )
            return JsonResponse({'success': True, 'message': 'Payout requested successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'errors': form.errors})

@login_required
@require_POST
def request_invoice(request):
    """Handle invoice requests."""
    form = InvoiceRequestForm(request.POST)
    if form.is_valid():
        invoice_service = InvoiceService()
        try:
            period_start, period_end = get_period_dates(form.cleaned_data)
            invoice = invoice_service.generate_invoice_from_commissions(
                reseller=request.user.reseller_profile,
                period_start=period_start,
                period_end=period_end
            )
            return JsonResponse({'success': True, 'message': 'Invoice generated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'errors': form.errors})

def get_period_dates(data):
    """Determine the actual dates for the provided period."""
    if data['period'] == 'last_month':
        # Last month's period
        today = timezone.now().date()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        return first_day_last_month, last_day_last_month
    elif data['period'] == 'current_month':
        # Current month's period
        today = timezone.now().date()
        first_day_this_month = today.replace(day=1)
        return first_day_this_month, today
    elif data['period'] == 'custom':
        return data['from_date'], data['to_date']
    else:
        raise ValueError('Invalid period selection.')
