from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..services.subscription_service import SubscriptionService

@login_required
def my_plans(request):
    service = SubscriptionService()
    dashboard_data = service.get_subscription_dashboard_data(request.user)
    
    context = {
        'page_title': 'My Subscriptions',
        'subscriptions': dashboard_data['subscriptions'],
        'total_monthly_cost': dashboard_data['total_monthly_cost'],
        'analytics': dashboard_data['analytics']
    }
    
    return render(request, 'dashboards/business/pages/my-plans.html', context)