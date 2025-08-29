from django.urls import path
from .views.subscription_views import my_plans
from .api.v1.views.subscription_apiviews import get_subscription_data, upgrade_subscription
from .api.v1.views.subscription_user_apiviews import add_subscription_user, remove_subscription_user
from .api.v1.views.billing_apiviews import initiate_payment, mpesa_payment


app_name = 'business'

urlpatterns = [
    path('my-plans/', my_plans, name='my-plans'),
    path('api/v1/subscriptions/', get_subscription_data, name='api-subscriptions'),
    path('api/v1/subscriptions/<int:subscription_id>/upgrade/', 
         upgrade_subscription, name='api-subscription-upgrade'),
    path('api/v1/subscriptions/<int:subscription_id>/users/add/', 
         add_subscription_user, name='api-subscription-add-user'),
    path('api/v1/subscriptions/<int:subscription_id>/users/<int:user_id>/remove/', 
         remove_subscription_user, name='api-subscription-remove-user'), 
    path('api/v1/billing/initiate-payment/', 
         initiate_payment, name='api-initiate-payment'),
    path('api/v1/billing/mpesa-payment/', 
         mpesa_payment, name='api-mpesa-payment'),         
]