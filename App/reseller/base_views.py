from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .earnings.models import Reseller, Commission, Invoice, Payout
from .earnings.services import CommissionService, InvoiceService, PayoutService
from .earnings.repositories import CommissionRepository, InvoiceRepository, PayoutRepository
from .utils import generate_partner_code

@login_required
def dashboard(request):
    """Reseller dashboard view"""
    try:
        reseller = Reseller.objects.get(user=request.user)
        referral_code = reseller.referral_code
    except Reseller.DoesNotExist:
        # Create a default reseller profile if it doesn't exist
        reseller = Reseller.objects.create(
            user=request.user,
            referral_code=Reseller.generate_unique_referral_code(request.user.id),
            tier='bronze',
            commission_rate=10.00
        )
        referral_code = reseller.referral_code
    
    # Build recent transactions from real commissions
    from .earnings.models import Commission
    recent_commissions = Commission.objects.filter(reseller=reseller).order_by('-calculation_date')[:10]
    status_color_map = {
        'paid': 'success',
        'approved': 'info',
        'pending': 'warning',
        'rejected': 'danger',
    }
    recent_transactions = [
        {
            'id': c.id,
            'amount': float(c.amount),
            'date': c.calculation_date,
            'status': c.status,
            'status_color': status_color_map.get(c.status, 'secondary'),
        }
        for c in recent_commissions
    ]

    # Map tier name
    tier_names = {
        'bronze': 'Bronze Partner',
        'silver': 'Silver Partner',
        'gold': 'Gold Partner',
        'platinum': 'Platinum Partner',
    }

    context = {
        'current_tier': tier_names.get(reseller.tier, reseller.tier),
        'total_commission': str(reseller.total_commission_earned),
        'subscription_level': '',
        'referral_code': referral_code,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'dashboards/reseller/reseller-dashboard.html', context)

@login_required
def leads(request):
    """Lead management page"""
    return render(request, 'dashboards/reseller/pages/sales/leads.html')

@login_required
def referrals(request):
    """Referrals tracking page"""
    return render(request, 'dashboards/reseller/pages/sales/referrals.html')

@login_required
def reports(request):
    """Sales reports page"""
    return render(request, 'dashboards/reseller/pages/sales/reports.html')

@login_required
def earnings(request):
    """Earnings overview page"""
    return render(request, 'dashboards/reseller/pages/dashboard.html')

@login_required
def commissions(request):
    """Commission overview page"""
    try:
        reseller = Reseller.objects.get(user=request.user)
    except Reseller.DoesNotExist:
        # Create a default reseller profile if it doesn't exist
        from django.contrib import messages
        messages.warning(request, "Please complete your reseller profile to view commissions.")
        # For now, create a basic profile
        reseller = Reseller.objects.create(
            user=request.user,
            referral_code=Reseller.generate_unique_referral_code(request.user.id),
            tier='bronze',
            commission_rate=10.00
        )
    
    commission_service = CommissionService()
    commission_repo = CommissionRepository()

    # Filters and search
    filters = {
        'status': request.GET.get('status'),
        'month': request.GET.get('month')
    }
    search_term = request.GET.get('search')
    
    # Get commissions with filters
    commissions = commission_repo.get_reseller_commissions(reseller, filters)
    if search_term:
        commissions = commission_repo.search_commissions(reseller, search_term)

    # Pagination setup
    page_number = request.GET.get('page', 1)
    paginator = Paginator(commissions, 10)
    page_obj = paginator.get_page(page_number)

    # Commission summary
    summary = commission_service.get_commission_summary(reseller)
    
    # Calculate current month earnings
    current_date = timezone.now()
    current_month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_commissions = commission_repo.get_reseller_commissions(
        reseller, 
        {'created_at__gte': current_month_start}
    )
    current_month_earnings = sum(c.amount for c in current_month_commissions)
    
    # Calculate previous month earnings for growth
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start - timedelta(seconds=1)
    last_month_commissions = commission_repo.get_reseller_commissions(
        reseller,
        {'created_at__gte': last_month_start, 'created_at__lte': last_month_end}
    )
    last_month_earnings = sum(c.amount for c in last_month_commissions)
    
    # Calculate monthly growth
    if last_month_earnings > 0:
        monthly_growth = ((current_month_earnings - last_month_earnings) / last_month_earnings) * 100
    else:
        monthly_growth = 100 if current_month_earnings > 0 else 0
    
    # Calculate pending amount
    pending_commissions = commission_repo.get_reseller_commissions(
        reseller,
        {'status': 'pending'}
    )
    pending_amount = sum(c.amount for c in pending_commissions)
    
    # Calculate lifetime earnings
    lifetime_earnings = reseller.total_commission_earned
    
    # Tier information
    tier_map = {
        'bronze': {'name': 'Bronze Partner', 'icon': 'bronze', 'next': 'Silver', 'threshold': 10000},
        'silver': {'name': 'Silver Partner', 'icon': 'silver', 'next': 'Gold', 'threshold': 50000},
        'gold': {'name': 'Gold Partner', 'icon': 'gold', 'next': 'Platinum', 'threshold': 100000},
        'platinum': {'name': 'Platinum Partner', 'icon': 'platinum', 'next': None, 'threshold': None}
    }
    current_tier_info = tier_map.get(reseller.tier, tier_map['bronze'])
    
    # Calculate tier progress
    if current_tier_info['threshold']:
        tier_progress = min((lifetime_earnings / current_tier_info['threshold']) * 100, 100)
        amount_to_next_tier = max(current_tier_info['threshold'] - lifetime_earnings, 0)
    else:
        tier_progress = 100
        amount_to_next_tier = 0
    
    # Recent activity (last 5 commissions)
    recent_activity = list(commissions[:5])
    
    # Format dates for chart labels (last 7 days)
    chart_dates = [(current_date - timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)]
    
    context = {
        'page_obj': page_obj,
        'filters': filters,
        'search_term': search_term,
        'current_month_earnings': current_month_earnings,
        'monthly_growth': monthly_growth,
        'pending_amount': pending_amount,
        'lifetime_earnings': lifetime_earnings,
        'current_tier': current_tier_info['name'],
        'tier_icon': current_tier_info['icon'],
        'next_tier': current_tier_info['next'],
        'tier_progress': tier_progress,
        'amount_to_next_tier': amount_to_next_tier,
        'recent_activity': recent_activity,
        'chart_dates': chart_dates,
        'commission_rate': reseller.commission_rate,
        'total_transactions': summary['count'],
        'status_breakdown': summary['status_breakdown']
    }
    return render(request, 'dashboards/reseller/pages/earnings/commissions.html', context)

@login_required
def invoices(request):
    """Invoice history page"""
    try:
        reseller = Reseller.objects.get(user=request.user)
    except Reseller.DoesNotExist:
        from django.contrib import messages
        messages.warning(request, "Please complete your reseller profile to view invoices.")
        reseller = Reseller.objects.create(
            user=request.user,
            referral_code=Reseller.generate_unique_referral_code(request.user.id),
            tier='bronze',
            commission_rate=10.00
        )
    invoice_service = InvoiceService()
    invoice_repo = InvoiceRepository()

    # Filters and search
    filters = {
        'status': request.GET.get('status'),
        'year': request.GET.get('year')
    }
    search_term = request.GET.get('search')

    # Get invoices with filters
    invoices = invoice_repo.get_reseller_invoices(reseller, filters)
    if search_term:
        invoices = invoice_repo.search_invoices(reseller, search_term)

    # Pagination setup
    page_number = request.GET.get('page', 1)
    paginator = Paginator(invoices, 10)
    page_obj = paginator.get_page(page_number)

    # Invoice summary
    available_years = invoice_repo.get_available_years(reseller)
    summary = invoice_service.get_invoice_summary(reseller)

    context = {
        'page_obj': page_obj,
        'summary': summary,
        'filters': filters,
        'search_term': search_term,
        'available_years': available_years,
        'request_invoice_modal': True
    }
    return render(request, 'dashboards/reseller/pages/earnings/invoices.html', context)

@login_required
def payouts(request):
    """Payout history page"""
    try:
        reseller = Reseller.objects.get(user=request.user)
    except Reseller.DoesNotExist:
        from django.contrib import messages
        messages.warning(request, "Please complete your reseller profile to view payouts.")
        reseller = Reseller.objects.create(
            user=request.user,
            referral_code=Reseller.generate_unique_referral_code(request.user.id),
            tier='bronze',
            commission_rate=10.00
        )
    payout_service = PayoutService()
    payout_repo = PayoutRepository()

    # Filters
    filters = {
        'status': request.GET.get('status')
    }
    
    # Get payouts with filters
    payouts = payout_repo.get_reseller_payouts(reseller, filters)

    # Pagination setup
    page_number = request.GET.get('page', 1)
    paginator = Paginator(payouts, 10)
    page_obj = paginator.get_page(page_number)

    # Payout summary
    summary = payout_service.get_payout_summary(reseller)

    context = {
        'page_obj': page_obj,
        'summary': summary,
        'filters': filters,
        'request_payout_modal': True
    }
    return render(request, 'dashboards/reseller/pages/earnings/payouts.html', context)

@login_required
def links(request):
    """Referral links page"""
    return render(request, 'dashboards/reseller/pages/marketing/links.html')

@login_required
def tools(request):
    """Marketing tools page"""
    return render(request, 'dashboards/reseller/pages/marketing/tools.html')

@login_required
def resources(request):
    """Training resources page"""
    return render(request, 'dashboards/reseller/pages/marketing/resources.html')

@login_required
def settings(request):
    """Settings page"""
    # For now, redirect to dashboard
    return render(request, 'dashboards/reseller/reseller-dashboard.html')
