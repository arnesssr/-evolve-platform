from django.contrib import admin
from django.urls import path, include
from App import views

urlpatterns = [
    path('', views.landing_page, name = 'landing'),
    path('admin/', admin.site.urls),

    # Register & OTP Flow
    path('register/', views.register_view, name='register'),
    path('register-user/', views.register_user, name='register_user'),  
    path('verify_register_otp/', views.verify_register_otp, name='verify_register_otp'),
    path('resend_register_otp/', views.resend_register_otp, name='resend_register_otp'),  # NEW: Resend OTP for registration

    # Login & OTP Flow
    path('login/', views.login_user, name='login'),
    path('verify_login_otp/', views.verify_login_otp, name='verify_login_otp'),
    path('resend_login_otp/', views.resend_login_otp, name='resend_login_otp'),  # NEW: Resend OTP for login
    path('admin-login/', views.login_user, name='admin_login'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    
    # Password Reset URLs
    path('api/password-reset/send-code/', views.send_password_reset_code, name='send_password_reset_code'),
    path('api/password-reset/verify-code/', views.verify_password_reset_code, name='verify_password_reset_code'),
    path('api/password-reset/reset/', views.reset_password, name='reset_password'),
    path('api/password-reset/resend-code/', views.resend_password_reset_code, name='resend_password_reset_code'),
    path('onboarding/', views.onboarding, name='onboarding'),

    #pesapal urls
    path('payment/', views.payment, name='payment'),
    path('token/', views.get_token_view, name='get_token'),
    path('ipn/register/', views.register_ipn_view, name='register_ipn'),
    path('ipn/list/', views.list_ipns_view, name='list_ipns'),
    path('order/submit/', views.create_order_view, name='create_order'),
    path('ipn/', views.ipn_listener, name='ipn_listener'),
    path('payment/confirm', views.payment_confirm, name='payment_confirm'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    path('logout/', views.logout, name='logout'),
    
    # Business Dashboard URLs
    path('business-dashboard/', views.business_dashboard, name='business-dashboard'),
    path('business-subscriptions/', views.business_subscriptions, name='business-subscriptions'),
    path('business-billing/', views.business_billing, name='business-billing'),
    path('business-software-hub/', views.business_software_hub, name='business-software-hub'),
    path('business-users/', views.business_users, name='business-users'),
    path('business-support/', views.business_support, name='business-support'),
    path('business-settings/', views.business_settings, name='business-settings'),
    path('business-purchase/', views.business_purchase_software, name='business-purchase'),
    
    path('reseller-dashboard/', views.reseller_dashboard, name='reseller-dashboard'),
    
    # Include reseller app URLs
    path('reseller/', include('App.reseller.urls')),
    
    # Include admin app URLs
    path('platform/admin/', include('App.admin.urls')),

    path('admin-test/', views.admin_test, name='admin-dashboard-test'),
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('edit-plans/', views.edit_plans, name='edit-plans'),
    path('api/plans/<int:plan_id>/', views.get_plan_data, name='get_plan_data'),
    path('api/plans/<int:plan_id>/update/', views.update_plan, name='update_plan'),
    path("api/plans/<int:pk>/", views.get_plan, name="get_plan"),
    path("api/plans/create/", views.create_plan, name="create_plan"),
    path("api/plans/active/", views.get_active_plans, name="get_active_plans"),

]