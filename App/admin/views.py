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

# User Management Views
@login_required
def users_list(request):
    """Users list view"""
    return render(request, 'dashboards/admin/pages/users/list.html')

@login_required
def users_profile(request, user_id=None):
    """User profile view"""
    return render(request, 'dashboards/admin/pages/users/profile.html')

@login_required
def users_roles(request):
    """User roles management"""
    return render(request, 'dashboards/admin/pages/users/roles.html')

@login_required
def users_permissions(request):
    """User permissions management"""
    return render(request, 'dashboards/admin/pages/users/permissions.html')

# Content Management Views
@login_required
def content_posts(request):
    """Content posts management"""
    return render(request, 'dashboards/admin/pages/content/posts.html')

@login_required
def content_categories(request):
    """Content categories management"""
    return render(request, 'dashboards/admin/pages/content/categories.html')

@login_required
def content_media(request):
    """Media management"""
    return render(request, 'dashboards/admin/pages/content/media.html')

@login_required
def content_comments(request):
    """Comments moderation"""
    return render(request, 'dashboards/admin/pages/content/comments.html')

# E-commerce Views
@login_required
def ecommerce_products(request):
    """Products management"""
    return render(request, 'dashboards/admin/pages/ecommerce/products.html')

@login_required
def ecommerce_orders(request):
    """Orders management"""
    return render(request, 'dashboards/admin/pages/ecommerce/orders.html')

@login_required
def ecommerce_inventory(request):
    """Inventory management"""
    return render(request, 'dashboards/admin/pages/ecommerce/inventory.html')

@login_required
def ecommerce_discounts(request):
    """Discounts management"""
    return render(request, 'dashboards/admin/pages/ecommerce/discounts.html')

# Financial Views
@login_required
def financial_overview(request):
    """Financial overview"""
    return render(request, 'dashboards/admin/pages/financial/overview.html')

@login_required
def financial_payouts(request):
    """Payouts management"""
    return render(request, 'dashboards/admin/pages/financial/payouts.html')

@login_required
def financial_invoices(request):
    """Invoices management"""
    return render(request, 'dashboards/admin/pages/financial/invoices.html')

@login_required
def financial_transactions(request):
    """Transactions view"""
    return render(request, 'dashboards/admin/pages/financial/transactions.html')

# Analytics Views
@login_required
def analytics_overview(request):
    """Analytics overview"""
    return render(request, 'dashboards/admin/pages/analytics/overview.html')

@login_required
def analytics_users(request):
    """User analytics"""
    return render(request, 'dashboards/admin/pages/analytics/users.html')

@login_required
def analytics_content(request):
    """Content analytics"""
    return render(request, 'dashboards/admin/pages/analytics/content.html')

@login_required
def analytics_sales(request):
    """Sales analytics"""
    return render(request, 'dashboards/admin/pages/analytics/sales.html')

# Reports Views
@login_required
def reports_generate(request):
    """Report generation"""
    return render(request, 'dashboards/admin/pages/reports/generate.html')

@login_required
def reports_scheduled(request):
    """Scheduled reports"""
    return render(request, 'dashboards/admin/pages/reports/scheduled.html')

# Settings Views
@login_required
def settings_general(request):
    """General settings"""
    return render(request, 'dashboards/admin/pages/settings/general.html')

@login_required
def settings_security(request):
    """Security settings"""
    return render(request, 'dashboards/admin/pages/settings/security.html')

@login_required
def settings_notifications(request):
    """Notification settings"""
    return render(request, 'dashboards/admin/pages/settings/notifications.html')

@login_required
def settings_integrations(request):
    """Integration settings"""
    return render(request, 'dashboards/admin/pages/settings/integrations.html')

# System Views
@login_required
def system_logs(request):
    """System logs"""
    return render(request, 'dashboards/admin/pages/system/logs.html')

@login_required
def system_backup(request):
    """System backup"""
    return render(request, 'dashboards/admin/pages/system/backup.html')

@login_required
def system_maintenance(request):
    """System maintenance"""
    return render(request, 'dashboards/admin/pages/system/maintenance.html')
