from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from datetime import datetime, timedelta
import json

User = get_user_model()

# Create your admin views here.

@login_required
def dashboard(request):
    """Main admin dashboard view"""
    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_revenue': 0,  # Placeholder - integrate with your payment model
        'pending_requests': 0,  # Placeholder - integrate with your request model
    }
    return render(request, 'dashboards/admin/index.html', context)

# Users Management - map to existing templates
@login_required
def businesses_list(request):
    return render(request, 'dashboards/admin/pages/businesses/list.html')

@login_required
def businesses_detail(request, user_id=None):
    from App.models import Business
    context = {}
    if user_id is not None:
        try:
            b = Business.objects.get(pk=user_id)
            # Map to template-expected keys while preserving fallbacks in template
            context['business'] = {
                'company_name': b.business_name,
                'industry': b.industry,
                'company_size': b.company_size,
                'address_line1': '',
                'address_line2': '',
                'city': '',
                'state': '',
                'postal_code': b.postal_code,
                'country': b.country,
                'contact_person': '',
                'contact_title': '',
                'contact_email': b.business_email,
                'contact_phone': '',
                'created_date': b.created_at.strftime('%b %d, %Y') if hasattr(b, 'created_at') and b.created_at else '',
            }
            # Some shared modals expect a reseller object; provide a placeholder to avoid reverse errors
            context['reseller'] = {'id': user_id}
        except Business.DoesNotExist:
            pass
    return render(request, 'dashboards/admin/pages/businesses/detail.html', context)

@login_required
def resellers_list(request):
    return render(request, 'dashboards/admin/pages/resellers/list.html')

@login_required
def resellers_detail(request, user_id=None):
    return render(request, 'dashboards/admin/pages/resellers/detail.html')

@login_required
def admins_list(request):
    return render(request, 'dashboards/admin/pages/admins/list.html')

@login_required
def admins_detail(request, user_id=None):
    return render(request, 'dashboards/admin/pages/admins/form.html')

# Products & Plans
@login_required
def products_list(request):
    # Provide real products to the template if the Product model exists
    context = {}
    try:
        from App.models import Product
        context['products'] = Product.objects.all().order_by('-created_at')
    except Exception:
        context['products'] = []
    return render(request, 'dashboards/admin/pages/products/list.html', context)

@login_required
def products_form(request):
    return render(request, 'dashboards/admin/pages/products/form.html')

@login_required
def plans_list(request):
    context = {}
    try:
        from App.models import Plan
        context['plans'] = Plan.objects.all().order_by('display_order', 'name')
    except Exception:
        context['plans'] = []
    return render(request, 'dashboards/admin/pages/plans/list.html', context)

@login_required
def plans_form(request):
    return render(request, 'dashboards/admin/pages/plans/form.html')

# Financial Views
@login_required
def financial_revenue(request):
    return render(request, 'dashboards/admin/pages/financial/revenue.html')

@login_required
def financial_commissions(request):
    return render(request, 'dashboards/admin/pages/financial/commissions.html')

@login_required
def financial_payouts(request):
    return render(request, 'dashboards/admin/pages/financial/payouts.html')

@login_required
def financial_invoices(request):
    return render(request, 'dashboards/admin/pages/financial/invoices.html')

@login_required
def financial_transactions(request):
    return render(request, 'dashboards/admin/pages/financial/transactions.html')

# Analytics Views
@login_required
def analytics_overview(request):
    return render(request, 'dashboards/admin/pages/analytics/overview.html')

# Reports Views
@login_required
def reports_generate(request):
    return render(request, 'dashboards/admin/pages/reports/generate.html')

@login_required
def reports_scheduled(request):
    return render(request, 'dashboards/admin/pages/reports/scheduled.html')

# Settings Views
@login_required
def settings_general(request):
    return render(request, 'dashboards/admin/pages/settings/general.html')

@login_required
def settings_security(request):
    return render(request, 'dashboards/admin/pages/settings/security.html')

@login_required
def settings_notifications(request):
    return render(request, 'dashboards/admin/pages/settings/notifications.html')

@login_required
def settings_integrations(request):
    return render(request, 'dashboards/admin/pages/settings/integrations.html')

# System Views
@login_required
def system_status(request):
    return render(request, 'dashboards/admin/pages/system/status.html')

@login_required
def system_logs(request):
    return render(request, 'dashboards/admin/pages/system/logs.html')

@login_required
def system_backup(request):
    return render(request, 'dashboards/admin/pages/system/backup.html')

@login_required
def system_maintenance(request):
    return render(request, 'dashboards/admin/pages/system/maintenance.html')

