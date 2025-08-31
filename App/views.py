from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.decorators.http import require_http_methods
from django.conf import settings

from App.models import OTP
from App.models import UserProfile 
from App.models import Business, Plan, Feature, Subscription
from App.integrations.utils import send_otp, send_mail
from django.views.generic import TemplateView
from django.http import JsonResponse, Http404
from App.integrations import pesapal_service
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import uuid
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.
def login_view(request):
    return render(request, 'auth/login.html')

def logout(request):
    return redirect('/login/')

def register_view(request):
    return render(request, 'auth/register.html')

def register_user(request):
    if request.method == "POST":
        role = request.POST.get("role")
        industry = request.POST.get ("industry")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone") 
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            return render(request, "auth/register.html", {"error": "Passwords do not match."})

        if User.objects.filter(username=email).exists():
            return render(request, "auth/register.html", {"error": "User already exists."})

        # Temporarily store credentials in session
        request.session['reg_role'] = role
        request.session['reg_industry'] = industry
        request.session['reg_email'] = email
        request.session['reg_password'] = password
        request.session['reg_first_name'] = first_name
        request.session['reg_last_name'] = last_name
        request.session['reg_phone'] = phone

        otp = OTP.objects.create(email=email, purpose='register')
        send_otp(email, phone, otp.code)


        return redirect('verify_register_otp')

    return render(request, "auth/register.html")

def verify_register_otp(request):
    role = request.session.get('reg_role')
    industry = request.session.get('reg_industry')
    email = request.session.get('reg_email')
    password = request.session.get('reg_password')
    first_name = request.session.get('reg_first_name')
    last_name = request.session.get('reg_last_name')
    phone = request.session.get('reg_phone')

    if not email or not password or not first_name or not last_name or not phone:
        return redirect('register')

    if request.method == "POST":
        code = request.POST.get("otp")

        try:
            otp = OTP.objects.get(email=email, code=code, purpose="register", is_verified=False)
            if otp.is_expired():
                return render(request, "auth/verify_otp.html", 
                    {"error": "OTP expired.",
                    "action": "verify_register_otp"}
                    )

            otp.is_verified = True
            otp.save()

            user = User.objects.create_user( 
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
            )

            # Save other fields to profile
            from App.models import UserProfile
            UserProfile.objects.create(user=user, phone=phone, role=role, industry=industry)

            login(request, user)

            # Clear session
            for key in ['reg_email', 'reg_password', 'reg_first_name', 'reg_last_name', 'reg_phone']:
                request.session.pop(key, None)

            return redirect('onboarding')
        except OTP.DoesNotExist:
            return render(request, "auth/verify_otp.html",
                    {"error": "Invalid OTP.",
                    "action": "verify_register_otp"}
)

    return render(request, 'auth/verify_otp.html', {'action': 'verify_register_otp'})

def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")

        user_exists = User.objects.filter(username=email).exists()

        if user_exists:
            user = authenticate(request, username=email, password=password)
            if user:
                try:
                    profile = UserProfile.objects.get(user=user)
                    phone = profile.phone
                except UserProfile.DoesNotExist:
                    phone = None

                otp = OTP.objects.create(email=email, purpose='login')

                if phone:
                    send_otp(email, phone, otp.code)
                else:
                    send_mail(email, otp.code)

                request.session['otp_user_email'] = email
                request.session['otp_user_password'] = password
                return redirect('verify_login_otp')
            else:
                # Wrong password
                return render(request, "auth/login.html", {"error": "Incorrect password. Please try again."})
        else:
            # Email/user does not exist
            return render(request, "auth/login.html", {"error": "Email not found or invalid."})

    # Handle GET request
    return render(request, "auth/login.html")


def forgot_password(request):
    """
    Render the forgot password page.
    """
    return render(request, "auth/forgot-password.html")

def verify_login_otp(request):
    email = request.session.get('otp_user_email')
    password = request.session.get('otp_user_password')

    if not email or not password:
        return redirect('login')

    if request.method == "POST":
        code = request.POST.get("otp")

        try:
            otp = OTP.objects.get(email=email, code=code, purpose='login', is_verified=False)

            if otp.is_expired():
                return render(request, "auth/verify_otp.html",
                        {"error": "OTP expired.",
                        "action": "verify_login_otp"}
)

            otp.is_verified = True
            otp.save()

            user = authenticate(request, username=email, password=password)
            if user:
                try:
                    profile = UserProfile.objects.get(user=user)
                except UserProfile.DoesNotExist:
                    # If profile doesn't exist, create a default one or redirect to complete registration
                    return redirect('register')
                
                login(request, user)
                request.session.pop('otp_user_email', None)
                request.session.pop('otp_user_password', None)

                if profile.role == 'business_owner':
                     return redirect('business-dashboard')
                elif profile.role == 'admin':
                    return redirect('admin-dashboard')  
                else:
                    return redirect('reseller-dashboard')

        except OTP.DoesNotExist:
            return render(request, "auth/verify_otp.html", 
                        {"error": "Invalid OTP.",
                        "action": "verify_login_otp"}
)

    return render(request, 'auth/verify_otp.html', {'action': 'verify_login_otp'})


def landing_page(request):
    return render(request, 'landing/landing.html')

@login_required
def onboarding(request):
    user = request.user
    
    # Handle case where UserProfile doesn't exist
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If no profile exists, redirect to register to complete profile creation
        return redirect('register')

    if profile.role != 'business_owner':
        return redirect('reseller-dashboard')

    if request.method == "POST":
        business = Business(
            business_name = request.POST['business_name'],
            business_email = request.POST['business_email'],
            industry = request.POST['industry'],
            company_size = request.POST['company_size'],
            country = request.POST['country'],
            postal_code = request.POST['postal_code'],
        )
        business.save()
        return redirect('payment')
         
    return render(request, 'onboarding/onboarding.html')

def payment(request):
    # Get purchase context from session if available
    purchase_context = {
        'software': request.session.get('purchase_software'),
        'plan': request.session.get('purchase_plan'),
        'billing': request.session.get('purchase_billing'),
        'users': request.session.get('purchase_users'),
        'amount': request.session.get('purchase_amount'),
        'description': request.session.get('purchase_description')
    }
    
    # If we have purchase context, pass it to the template
    context = {}
    if purchase_context['software']:
        context['purchase'] = purchase_context
    
    return render(request, 'payments/payment.html', context)


def get_token_view(request):
    token = pesapal_service.generate_access_token()
    return JsonResponse({"token": token})

def register_ipn_view(request):
    token = pesapal_service.generate_access_token()
    ipn_url = request.GET.get("url")
    res = pesapal_service.register_ipn_url(token, ipn_url)
    return JsonResponse(res.json(), status=res.status_code)

def list_ipns_view(request):
    token = pesapal_service.generate_access_token()
    res = pesapal_service.get_registered_ipns(token)
    return JsonResponse(res.json(), safe=False)

@login_required
def register_current_ipn(request):
    """Register an IPN URL based on current host or override via ?host= param.
    Useful to quickly register https://<host>/ipn/ with Pesapal.
    """
    token = pesapal_service.generate_access_token()
    host = request.GET.get('host') or request.get_host()
    # Default to https scheme for production
    ipn_url = f"https://{host}/ipn/"
    res = pesapal_service.register_ipn_url(token, ipn_url)
    try:
        payload = res.json()
    except Exception:
        payload = {'status_code': res.status_code}
    return JsonResponse({'requested_url': ipn_url, 'status_code': res.status_code, 'response': payload}, status=res.status_code)

def create_order_view(request):
    token = pesapal_service.generate_access_token()
    
    # Log token status for debugging
    if not token:
        print("[PESAPAL] Failed to generate access token")
        return JsonResponse({"error": "Failed to authenticate with payment provider"}, status=500)
    
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
    else:
        amount = float(request.POST.get('amount', 0))
    
    # Use purchase context for description if available
    description = request.session.get('purchase_description', 'Payment description goes here')
    
    # If no amount provided but we have purchase amount in session, use it
    if amount == 0:
        amount = request.session.get('purchase_amount', 0)

    # Build a callback URL to our confirmation endpoint so we can verify and activate subscriptions
    callback_url = request.build_absolute_uri(reverse('payment_confirm'))

    # Attach affiliate markers if present for downstream reconciliation (non-authoritative)
    affiliate_code = request.session.get('affiliate_code') or request.COOKIES.get('affiliate_code')
    if affiliate_code:
        description = f"{description} | AFF={affiliate_code}"

    # Build a merchant reference that embeds the user id for reliable postback handling
    if request.user.is_authenticated:
        merchant_ref = f"U{request.user.id}-{uuid.uuid4()}"
        request.session['last_order_user_id'] = request.user.id
    else:
        merchant_ref = str(uuid.uuid4())

    # Derive payer info
    payer_email = getattr(request.user, 'email', '') if request.user.is_authenticated else ''
    payer_phone = ''
    try:
        from App.models import UserProfile as UP
        if request.user.is_authenticated:
            prof = UP.objects.filter(user=request.user).first()
            if prof and prof.phone:
                payer_phone = prof.phone
    except Exception:
        payer_phone = ''

    # Use merchant_reference as merchant_ref was renamed
    merchant_reference = merchant_ref
    email_address = payer_email
    phone = payer_phone

    payload = {
        "id": merchant_reference,
        "currency": "KES",
        "amount": amount,
        "description": description,
        "callback_url": callback_url,
        "notification_id": getattr(settings, 'PESAPAL_NOTIFICATION_ID', ''),
        "billing_address": {
            "email_address": email_address,
            "phone_number": phone,
            "country_code": "KE",
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "line_1": "",
            "line_2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "zip_code": ""
        }
    }

    # Persist payment initiation for billing history
    try:
        from App.models import PaymentRecord
        if request.user.is_authenticated:
            PaymentRecord.objects.create(
                user=request.user,
                order_id=merchant_ref,
                amount=amount,
                currency='KES',
                description=description,
                phone_number=payer_phone,
                plan_name=str(request.session.get('purchase_plan') or ''),
                billing=str(request.session.get('purchase_billing') or 'monthly'),
                payment_method='pesapal',
                status='initiated'
            )
    except Exception as e:
        print(f"PaymentRecord create error: {e}")

    res = pesapal_service.submit_order_request(token, payload)
    
    # Log response for debugging
    print(f"[PESAPAL] Order submission response code: {res.status_code}")
    
    try:
        res_json = res.json()
    except Exception as e:
        print(f"[PESAPAL] Failed to parse response JSON: {e}")
        print(f"[PESAPAL] Response text: {res.text[:500]}...")  # First 500 chars
        return JsonResponse({"error": "Invalid response from payment provider"}, status=500)
    
    if res.status_code == 200 and "redirect_url" in res_json:
        return JsonResponse({
            "redirect_url": res_json["redirect_url"]
        })
    else:
        # Log the actual error from Pesapal
        error_msg = res_json.get('message', res_json.get('error', 'Unknown error'))
        print(f"[PESAPAL] Order submission failed: {error_msg}")
        print(f"[PESAPAL] Full response: {res_json}")
        return JsonResponse({"error": f"Payment provider error: {error_msg}"}, status=400)

@csrf_exempt
def ipn_listener(request):
    """
    Authoritative payment notification handler (IPN) for Pesapal.
    - Normalizes params.
    - Verifies status via get_transaction_status.
    - Marks PaymentRecord completed/failed (idempotent).
    - On COMPLETED, activates subscription and creates commission based on affiliate attribution.
    """
    # Normalize params (Pesapal may send different casings)
    tracking_id = (
        request.GET.get("order_tracking_id")
        or request.GET.get("OrderTrackingId")
        or request.GET.get("tracking_id")
        or request.GET.get("TrackingId")
    )
    merchant_reference = (
        request.GET.get("order_merchant_reference")
        or request.GET.get("OrderMerchantReference")
        or request.GET.get("merchant_reference")
        or request.GET.get("MerchantReference")
    )

    token = pesapal_service.generate_access_token()
    status = pesapal_service.get_transaction_status(token, tracking_id, merchant_reference)

    from App.models import PaymentRecord
    pr = None
    try:
        if merchant_reference:
            pr = PaymentRecord.objects.filter(order_id=merchant_reference).first()
    except Exception:
        pr = None

    # Update PaymentRecord status idempotently
    try:
        if pr:
            pr.provider_tracking_id = tracking_id or pr.provider_tracking_id
            pr.provider_status = status or pr.provider_status
            if status == 'COMPLETED':
                pr.status = 'completed'
            elif status == 'FAILED':
                pr.status = 'failed'
            pr.save(update_fields=['provider_tracking_id', 'provider_status', 'status', 'updated_at'])
    except Exception as e:
        print(f"IPN PaymentRecord update error: {e}")

    if status == 'COMPLETED':
        # Resolve user from merchant reference (U<id>-...)
        user_for_actions = None
        if merchant_reference and merchant_reference.startswith('U'):
            try:
                uid_part = merchant_reference.split('-', 1)[0][1:]
                uid = int(uid_part)
                user_for_actions = User.objects.get(id=uid)
            except Exception:
                user_for_actions = None
        if (not user_for_actions) and pr:
            user_for_actions = pr.user

        # Infer plan/billing from PaymentRecord.description if possible
        plan = Plan.objects.filter(is_active=True).order_by('display_order').first()
        billing = 'monthly'
        try:
            desc = (pr.description if pr else '') or ''
            if 'Yearly' in desc:
                billing = 'yearly'
            # Optional: extract plan name inside parentheses (... (PlanName))
            import re
            m = re.search(r'\(([^)]+)\)', desc)
            if m:
                plan_name = m.group(1)
                p2 = Plan.objects.filter(name=plan_name).first()
                if p2:
                    plan = p2
        except Exception:
            pass

        # Activate subscription (basic amount check: optional warning on mismatch)
        if user_for_actions and plan:
            # Basic validation: compare expected vs recorded amount when possible
            try:
                expected_amount = None
                if pr and pr.billing:
                    if pr.billing == 'yearly' and plan.yearly_price and plan.yearly_price > 0:
                        expected_amount = float(plan.yearly_price)
                    else:
                        expected_amount = float(plan.price)
                if expected_amount is not None and pr and pr.amount and float(pr.amount) != float(expected_amount):
                    print(f"[WARN] Payment amount mismatch for {merchant_reference}: recorded={pr.amount} expected={expected_amount}")
            except Exception:
                pass

            now = timezone.now()
            period = timedelta(days=365) if billing == 'yearly' else timedelta(days=30)
            Subscription.objects.update_or_create(
                user=user_for_actions,
                product='payroll',
                defaults={
                    'plan': plan,
                    'status': 'active',
                    'start_date': now,
                    'end_date': now + period,
                    'auto_renewal': True,
                }
            )

        # Create commission using AFF marker and MarketingLink mapping
        try:
            # Extract affiliate code from description: "... | AFF=CODE"
            affiliate_code = None
            desc = (pr.description if pr else '') or ''
            if 'AFF=' in desc:
                affiliate_code = desc.split('AFF=', 1)[1].strip()
            if affiliate_code:
                from App.reseller.marketing.models import MarketingLink as ML
                ml = ML.objects.filter(code=affiliate_code, is_active=True).first()
                if ml:
                    from App.reseller.earnings.models.reseller import Reseller as ResellerModel
                    from App.reseller.earnings.services.commission_service import CommissionService
                    reseller = ResellerModel.objects.get(id=ml.reseller_id)
                    sale_amount = float(pr.amount) if pr else (float(plan.yearly_price) if billing=='yearly' and plan and plan.yearly_price else (float(plan.price) if plan else 0))
                    commission_rate = float(reseller.get_tier_commission_rate())
                    client_name = (user_for_actions.get_full_name() or user_for_actions.username) if user_for_actions else ''
                    client_email = (user_for_actions.email if user_for_actions else '')
                    notes = f"link_code={affiliate_code}; product=payroll; billing={billing}"
                    CommissionService().create_commission({
                        'reseller': reseller,
                        'sale_amount': sale_amount,
                        'commission_rate': commission_rate,
                        'transaction_reference': tracking_id or merchant_reference or str(uuid.uuid4()),
                        'client_name': client_name,
                        'client_email': client_email,
                        'product_name': 'Payroll Subscription',
                        'product_type': 'subscription',
                        'notes': notes,
                    })
        except Exception as e:
            print(f"IPN Commission creation error: {e}")

        return HttpResponse("OK", status=200)

    # Non-completed or failed status
    return HttpResponse("IGNORED", status=200)

def payment_confirm(request):
    # Provider may send different param names; normalize them
    tracking_id = (
        request.GET.get("order_tracking_id")
        or request.GET.get("OrderTrackingId")
        or request.GET.get("tracking_id")
        or request.GET.get("TrackingId")
    )
    merchant_reference = (
        request.GET.get("order_merchant_reference")
        or request.GET.get("OrderMerchantReference")
        or request.GET.get("merchant_reference")
        or request.GET.get("MerchantReference")
    )

    token = pesapal_service.generate_access_token()
    status = pesapal_service.get_transaction_status(token, tracking_id, merchant_reference)

    # Try to update stored PaymentRecord
    try:
        from App.models import PaymentRecord
        pr = None
        if merchant_reference:
            pr = PaymentRecord.objects.filter(order_id=merchant_reference).first()
        if pr:
            pr.provider_tracking_id = tracking_id or pr.provider_tracking_id
            pr.provider_status = status or pr.provider_status
            if status == 'COMPLETED':
                pr.status = 'completed'
            elif status == 'FAILED':
                pr.status = 'failed'
            pr.save(update_fields=['provider_tracking_id', 'provider_status', 'status', 'updated_at'])
    except Exception as e:
        print(f"PaymentRecord update error: {e}")

    # Determine acting user (in case session/login was lost on redirect)
    user_for_actions = request.user if request.user.is_authenticated else None
    if not user_for_actions and merchant_reference and merchant_reference.startswith('U'):
        try:
            uid_part = merchant_reference.split('-', 1)[0][1:]
            uid = int(uid_part)
            user_for_actions = User.objects.get(id=uid)
        except Exception:
            pass
    if not user_for_actions:
        last_uid = request.session.get('last_order_user_id')
        if last_uid:
            try:
                user_for_actions = User.objects.get(id=last_uid)
            except Exception:
                user_for_actions = None

    if status == "COMPLETED":
        # On successful payment, activate subscription if applicable
        software = request.session.get('purchase_software', 'payroll')
        plan_name = request.session.get('purchase_plan')
        billing = request.session.get('purchase_billing', 'monthly')
        if software == 'payroll' and user_for_actions:
            try:
                plan = Plan.objects.get(name=plan_name)
            except Plan.DoesNotExist:
                plan = Plan.objects.filter(is_active=True).order_by('display_order').first()
            now = timezone.now()
            period = timedelta(days=365) if billing == 'yearly' else timedelta(days=30)
            if plan:
                Subscription.objects.update_or_create(
                    user=user_for_actions,
                    product='payroll',
                    defaults={
                        'plan': plan,
                        'status': 'active',
                        'start_date': now,
                        'end_date': now + period,
                        'auto_renewal': True,
                    }
                )

            # Create reseller commission if attributed via short link
            try:
                affiliate_code = request.session.get('affiliate_code') or request.COOKIES.get('affiliate_code')
                affiliate_reseller_id = request.session.get('affiliate_reseller_id')
                from App.reseller.earnings.models.reseller import Reseller as ResellerModel
                from App.reseller.earnings.services.commission_service import CommissionService
                from App.reseller.earnings.models import Commission as CommissionModel
                if affiliate_code and not affiliate_reseller_id:
                    # Resolve reseller from MarketingLink
                    try:
                        from App.reseller.marketing.models import MarketingLink as ML
                        ml = ML.objects.filter(code=affiliate_code, is_active=True).first()
                        if ml:
                            affiliate_reseller_id = ml.reseller_id
                    except Exception:
                        affiliate_reseller_id = None
                if affiliate_reseller_id and affiliate_code:
                    # Ensure idempotency: skip if a commission already exists for this transaction reference
                    tx_ref = tracking_id or merchant_reference or str(uuid.uuid4())
                    if not CommissionModel.objects.filter(transaction_reference=tx_ref).exists():
                        reseller = ResellerModel.objects.get(id=affiliate_reseller_id)
                        # Determine sale amount (from session or plan)
                        sale_amount = request.session.get('purchase_amount')
                        if (not sale_amount) and plan:
                            sale_amount = float(plan.yearly_price) if billing == 'yearly' and plan.yearly_price else float(plan.price)
                        sale_amount = sale_amount or (pr.amount if pr else 0)
                        commission_rate = float(reseller.get_tier_commission_rate())
                        client_name = (user_for_actions.get_full_name() or user_for_actions.username)
                        client_email = user_for_actions.email
                        notes = f"link_code={affiliate_code}; product=payroll; billing={billing}"
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
            except Exception as e:
                # Do not fail user flow if commission creation fails
                print(f"Commission creation error: {e}")

        # Clear purchase context (keep affiliate cookie; session keys not needed anymore)
        for k in ['purchase_software','purchase_plan','purchase_billing','purchase_users','purchase_amount','purchase_description','last_order_user_id']:
            request.session.pop(k, None)
        # Friendly UX: send user to business dashboard (validated by active subscription)
        messages.success(request, 'Payment successful. Your Payroll subscription is now active.')
        return redirect('business-dashboard')
    else:
        messages.error(request, 'Payment could not be verified. Please contact support if you were charged.')
        return redirect('business-subscriptions')


@login_required
def business_dashboard(request):
    # Render the consolidated dashboard page template with subscription context
    payroll = None
    payroll_active = False
    try:
        payroll = Subscription.objects.filter(user=request.user, product='payroll').order_by('-end_date').first()
        if payroll and payroll.status == 'active' and payroll.end_date:
            payroll_active = payroll.end_date >= timezone.now()
    except Exception:
        payroll = None
        payroll_active = False
    context = {
        'payroll': payroll,
        'payroll_active': payroll_active,
    }
    return render(request, 'dashboards/business/pages/dashboard.html', context)

# Business Dashboard Views
@login_required
def business_subscriptions(request):
    payroll = None
    payroll_active = False
    try:
        payroll = Subscription.objects.filter(user=request.user, product='payroll').order_by('-end_date').first()
        if payroll and payroll.status == 'active' and payroll.end_date:
            payroll_active = payroll.end_date >= timezone.now()
    except Exception:
        payroll = None
        payroll_active = False
    context = {
        'payroll': payroll,
        'payroll_active': payroll_active,
    }
    return render(request, 'dashboards/business/pages/my-plans.html', context)

@login_required
def business_billing(request):
    # Show user's recent payments/invoices (from PaymentRecord)
    payments = []
    try:
        from App.models import PaymentRecord
        payments = PaymentRecord.objects.filter(user=request.user).order_by('-created_at')[:50]
    except Exception:
        payments = []
    return render(request, 'dashboards/business/pages/billing-history.html', { 'payments': payments })

@login_required
def business_billing_export(request):
    """Export user's PaymentRecord rows as CSV"""
    import csv
    from io import StringIO
    from django.http import HttpResponse as DjHttpResponse
    from App.models import PaymentRecord

    rows = PaymentRecord.objects.filter(user=request.user).order_by('-created_at')
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Invoice #', 'Date', 'Description', 'Amount', 'Currency', 'Status', 'Provider Status', 'Phone', 'Plan', 'Billing'])
    for p in rows:
        writer.writerow([
            p.order_id,
            p.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            p.description or '',
            str(p.amount),
            p.currency,
            p.status,
            p.provider_status or '',
            p.phone_number or '',
            p.plan_name or '',
            (p.billing or '').title(),
        ])
    resp = DjHttpResponse(output.getvalue(), content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="billing_statement.csv"'
    return resp

@login_required
def business_invoice_download(request, order_id: str):
    """Generate and download a PDF invoice/receipt for a PaymentRecord.
    Uses reportlab if available; otherwise returns a simple text fallback as PDF.
    """
    from App.models import PaymentRecord
    pr = get_object_or_404(PaymentRecord, user=request.user, order_id=order_id)

    # Try ReportLab
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from io import BytesIO
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Invoice / Receipt")
        y -= 30
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Invoice #: {pr.order_id}")
        y -= 15
        p.drawString(50, y, f"Date: {pr.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 15
        p.drawString(50, y, f"User: {request.user.email}")
        y -= 15
        p.drawString(50, y, f"Description: {pr.description or 'Payment'}")
        y -= 15
        p.drawString(50, y, f"Amount: {pr.currency} {pr.amount}")
        y -= 15
        p.drawString(50, y, f"Status: {pr.status.title()} (provider: {pr.provider_status or 'N/A'})")
        y -= 15
        p.drawString(50, y, f"Phone: {pr.phone_number or '—'}")
        y -= 15
        p.drawString(50, y, f"Plan: {pr.plan_name or '—'} | Billing: {(pr.billing or '').title()}")
        y -= 30
        p.setFont("Helvetica-Oblique", 9)
        p.drawString(50, y, "Thank you for your payment.")

        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=\"invoice_{pr.order_id}.pdf\"'
        return response
    except Exception:
        # Fallback: simple text with PDF content type (not ideal, but functional)
        content = (
            f"Invoice #: {pr.order_id}\n"
            f"Date: {pr.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"User: {request.user.email}\n"
            f"Description: {pr.description or 'Payment'}\n"
            f"Amount: {pr.currency} {pr.amount}\n"
            f"Status: {pr.status} (provider: {pr.provider_status or 'N/A'})\n"
            f"Phone: {pr.phone_number or '—'}\n"
            f"Plan: {pr.plan_name or '—'} | Billing: {(pr.billing or '').title()}\n"
        )
        response = HttpResponse(content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename=\"invoice_{pr.order_id}.txt\"'
        return response

@login_required
def business_users(request):
    return render(request, 'dashboards/business/pages/user-management.html')

@login_required
def business_support(request):
    return render(request, 'dashboards/business/pages/support-center.html')

@login_required
def business_settings(request):
    # Redirect to the main dashboard since settings is not implemented for MVP
    return render(request, 'dashboards/business/pages/dashboard.html')

@login_required
def business_purchase_software(request):
    """
    Handle software purchase requests - restrict to payroll only.
    This removes non-payroll product placeholders and simplifies logic per platform scope.
    """
    if request.method == "POST":
        # Force product to payroll regardless of incoming value
        software = 'payroll'
        plan = request.POST.get('plan', 'standard')
        billing = request.POST.get('billing', 'monthly')
        users = request.POST.get('users', '1')
        
        # Store purchase details in session for payment processing
        request.session['purchase_software'] = software
        request.session['purchase_plan'] = plan
        request.session['purchase_billing'] = billing
        request.session['purchase_users'] = users
        
        # Calculate pricing for payroll only
        pricing = {
            'payroll': {'standard': 5000, 'professional': 8000}
        }
        
        software_name_map = {
            'payroll': 'Payroll System'
        }
        
        base_cost = pricing['payroll'].get(plan, pricing['payroll']['standard'])
        setup_fee = 5000
        total_cost = base_cost + setup_fee
        
        # Apply yearly discount if applicable
        if billing == 'yearly':
            base_cost = int(base_cost * 12 * 0.85)  # 15% discount
            total_cost = base_cost + setup_fee
        
        # Store pricing for payment
        request.session['purchase_amount'] = total_cost
        request.session['purchase_description'] = f"{software_name_map['payroll']} - {plan.title()} Plan ({billing})"
        
        # Redirect to existing payment flow
        return redirect('payment')
    
    return redirect('business-dashboard')

@login_required
def subscribe_payroll(request):
    """Prepare a Payroll purchase based on active plan and redirect to payment."""
    billing = request.GET.get('billing', 'monthly')
    plan = Plan.objects.filter(is_active=True).order_by('display_order').first()
    if not plan:
        # No plan configured by admin yet
        return render(request, 'payments/payment-failed.html', { 'error': 'No active plan configured. Please contact support.' })

    # Compute amount from plan based on billing
    if billing == 'yearly' and plan.yearly_price and plan.yearly_price > 0:
        amount = float(plan.yearly_price)
    else:
        amount = float(plan.price)
        billing = 'monthly'

    # Store purchase details in session for payment processing
    request.session['purchase_software'] = 'payroll'
    request.session['purchase_plan'] = plan.name
    request.session['purchase_billing'] = billing
    request.session['purchase_users'] = '1'
    request.session['purchase_amount'] = amount
    request.session['purchase_description'] = f"Payroll System - {billing.title()} Plan ({plan.name})"

    return redirect('payment')

@login_required
def launch_payroll(request):
    """Gate Payroll launch behind an active subscription."""
    has_active = Subscription.objects.filter(
        user=request.user,
        product='payroll',
        status='active',
        end_date__gte=timezone.now()
    ).exists()
    if has_active:
        return redirect('/software/payroll/')
    else:
        return redirect('subscribe_payroll')

@login_required
def reseller_dashboard(request):
    return render(request, 'dashboards/reseller/reseller-dashboard.html')

def payment_failed(request):
    return render(request, 'payments/payment-failed.html')

@staff_member_required
def pesapal_health(request):
    """Check Pesapal configuration and connectivity.
    Returns JSON with:
    - token_ok: whether we obtained an access token
    - base_url: Pesapal base URL in use
    - notification_id_set: whether PESAPAL_NOTIFICATION_ID is configured
    - branch_set: whether PESAPAL_BRANCH is configured
    - ipn_list_ok: whether the IPN list endpoint responded OK
    - ipn_registered_for_host: whether an IPN exists matching https://<host>/ipn/
    """
    from django.http import JsonResponse
    from django.utils.timezone import now
    from App.integrations import pesapal_service
    import traceback

    result = {
        'checked_at': now().isoformat(),
        'base_url': getattr(settings, 'PESAPAL_BASE_URL', ''),
        'notification_id_set': bool(getattr(settings, 'PESAPAL_NOTIFICATION_ID', '')),
        'branch_set': bool(getattr(settings, 'PESAPAL_BRANCH', '')),
        'token_ok': False,
        'ipn_list_ok': False,
        'ipn_registered_for_host': False,
        'details': {},
    }

    try:
        token = pesapal_service.generate_access_token()
        result['token_ok'] = bool(token)
        if token:
            # Try listing IPNs
            resp = pesapal_service.get_registered_ipns(token)
            result['ipn_list_ok'] = (getattr(resp, 'status_code', 0) == 200)
            try:
                data = resp.json() if hasattr(resp, 'json') else []
            except Exception:
                data = []
            # Match expected URL for this host
            host = request.get_host()
            expected = f"https://{host}/ipn/"
            # Pesapal may return list of dicts; try to match by url field case-insensitively
            found = False
            if isinstance(data, list):
                for item in data:
                    url = (item.get('url') or item.get('Url') or '').strip()
                    if url.lower() == expected.lower():
                        found = True
                        break
            result['ipn_registered_for_host'] = found
            # Keep minimal diagnostics (no secrets)
            result['details']['ipn_count'] = len(data) if isinstance(data, list) else None
            result['details']['expected_ipn'] = expected
        else:
            result['details']['error'] = 'Failed to obtain access token; check PESAPAL_CONSUMER_KEY/SECRET and BASE_URL'
    except Exception as e:
        result['details']['exception'] = str(e)
        result['details']['trace'] = traceback.format_exc().splitlines()[-3:]

    return JsonResponse(result, status=200 if result['token_ok'] else 500)

def admin_dashboard(request):
    return render(request, 'dashboards/admin/dashboard.html')

from django.conf import settings
from django.db.models import F
from urllib.parse import urlparse
from App.reseller.marketing.models import MarketingLink

def link_redirect(request, code: str):
    """Resolve a marketing link code, increment click count, set attribution, and redirect safely.
    - Increments MarketingLink.clicks atomically.
    - Stores attribution in session and a cookie (affiliate_code) for 30 days.
    - Redirects only to same-origin destinations; otherwise falls back to '/'.
    """
    try:
        link = MarketingLink.objects.get(code=code, is_active=True)
    except MarketingLink.DoesNotExist:
        # Unknown or inactive code: send to a safe default (landing)
        return redirect('landing')

    # Increment clicks atomically
    MarketingLink.objects.filter(pk=link.pk).update(clicks=F('clicks') + 1)

    # Store attribution server-side
    request.session['affiliate_code'] = link.code
    request.session['affiliate_reseller_id'] = link.reseller_id

    # Build a safe redirect target (same host or relative URL only)
    target = link.destination_url or '/'
    try:
        parsed = urlparse(target)
        host = request.get_host()
        if parsed.netloc and parsed.netloc != host:
            # Disallow external redirects; fall back to homepage
            target = '/'
    except Exception:
        target = '/'

    # Prepare response and set cookie
    resp = redirect(target)
    max_age = 30 * 24 * 60 * 60  # 30 days
    secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
    samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax') or 'Lax'
    resp.set_cookie('affiliate_code', link.code, max_age=max_age, secure=secure, samesite=samesite)
    return resp

def edit_plans(request):
    plans = Plan.objects.all().order_by('display_order')
    return render(request, 'dashboards/admin/edit-plans.html', {'plans': plans})


def get_plan_data(request, plan_id):
    try:
        plan = Plan.objects.get(id=plan_id)
        features = plan.features.all()
        feature_list = [{"name": f.name, "value": f.value} for f in features]

        data = {
            "id": plan.id,
            "name": plan.name,
            "badge": plan.badge,
            "description": plan.description,
            "price": float(plan.price),
            "yearly_price": float(plan.yearly_price),
            "is_active": plan.is_active,
            "display_order": plan.display_order,
            "features": feature_list
        }
        return JsonResponse(data)
    except Plan.DoesNotExist:
        raise Http404("Plan not found")

@csrf_exempt
@require_http_methods(["POST"])
def update_plan(request, plan_id):
    try:
        data = json.loads(request.body)

        # Get and update the plan
        plan = Plan.objects.get(id=plan_id)
        plan.name = data.get('name')
        plan.badge = data.get('badge')
        plan.description = data.get('description')
        plan.price = data.get('price')
        plan.yearly_price = data.get('yearly_price')
        plan.is_active = data.get('is_active', True)
        plan.display_order = data.get('display_order', 0)
        plan.save()

        # Clear all existing features for this plan
        Feature.objects.filter(plan=plan).delete()

        # Recreate features from submitted data
        for feature in data.get('features', []):
            Feature.objects.create(
                plan=plan,
                name=feature['name'],
                value=feature['value']
            )

        return JsonResponse({'status': 'success', 'message': 'Plan updated'})

    except Plan.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Plan not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def create_plan(request):
    if request.method == "POST":
        data = json.loads(request.body)
        plan = Plan.objects.create(
            name=data.get("name", ""),
            badge=data.get("badge", ""),
            description=data.get("description", ""),
            price=data.get("price", 0),
            yearly_price=data.get("yearly_price", 0),
            is_active=data.get("is_active", True),
            display_order=data.get("display_order", 0)
        )
        return JsonResponse({"message": "Created", "id": plan.id}, status=201)
    return JsonResponse({"error": "Invalid method"}, status=405)

def get_plan(request, pk):
    plan = get_object_or_404(Plan, pk=pk)

    features = Feature.objects.filter(plan=plan).values('name', 'value')

    data = {
        'id': plan.id,
        'name': plan.name,
        'badge': plan.badge,
        'description': plan.description,
        'price': float(plan.price),
        'yearly_price': float(plan.yearly_price),
        'is_active': plan.is_active,
        'display_order': plan.display_order,
        'features': list(features)
    }

    return JsonResponse(data)

def get_active_plans(request):
    plans = Plan.objects.filter(is_active=True).order_by('display_order')
    plan_list = []
    for plan in plans:
        plan_list.append({
            'id': plan.id,
            'name': plan.name,
            'badge': plan.badge,
            'description': plan.description,
            'price': float(plan.price),
            'yearly_price': float(plan.yearly_price),
            'features': list(plan.features.values('name', 'value')),
        })
    return JsonResponse({'plans': plan_list})

# ==============================================================================
# NEW RESEND OTP FUNCTIONALITY - Added by AI Assistant on 2025-01-10
# ==============================================================================

def resend_register_otp(request):
    """
    Resends OTP for registration flow.
    Requires user data to be stored in session from register_user view.
    """
    # Get user data from session (set by register_user view)
    email = request.session.get('reg_email')
    phone = request.session.get('reg_phone')
    
    if not email or not phone:
        # Session expired or invalid, redirect to register
        return redirect('register')
    
    try:
        # Mark any existing unverified OTPs as expired by deleting them
        # This prevents accumulation of multiple active OTPs
        OTP.objects.filter(email=email, purpose='register', is_verified=False).delete()
        
        # Generate new OTP for registration
        otp = OTP.objects.create(email=email, purpose='register')
        
        # Send the new OTP via email and SMS
        send_otp(email, phone, otp.code)
        
        # Return success response
        return JsonResponse({
            'success': True, 
            'message': 'OTP resent successfully! Please check your email and SMS.'
        })
        
    except Exception as e:
        # Handle any errors during OTP generation or sending
        return JsonResponse({
            'success': False, 
            'message': 'Failed to resend OTP. Please try again.'
        }, status=500)

def resend_login_otp(request):
    """
    Resends OTP for login flow.
    Requires user credentials to be stored in session from login_user view.
    """
    # Get user credentials from session (set by login_user view)
    email = request.session.get('otp_user_email')
    password = request.session.get('otp_user_password')
    
    if not email or not password:
        # Session expired or invalid, redirect to login
        return redirect('login')
    
    try:
        # Verify user credentials again for security
        user = authenticate(request, username=email, password=password)
        if not user:
            # Invalid credentials, redirect to login
            return redirect('login')
        
        # Get user's phone number for SMS
        try:
            profile = UserProfile.objects.get(user=user)
            phone = profile.phone
        except UserProfile.DoesNotExist:
            phone = None
        
        # Mark any existing unverified OTPs as expired by deleting them
        # This prevents accumulation of multiple active OTPs
        OTP.objects.filter(email=email, purpose='login', is_verified=False).delete()
        
        # Generate new OTP for login
        otp = OTP.objects.create(email=email, purpose='login')
        
        # Send the new OTP via email and SMS (if phone available)
        if phone:
            send_otp(email, phone, otp.code)
        else:
            # Fallback to email-only if no phone number
            send_mail(email, otp.code)
        
        # Return success response
        return JsonResponse({
            'success': True, 
            'message': 'OTP resent successfully! Please check your email and SMS.'
        })
        
    except Exception as e:
        # Handle any errors during OTP generation or sending
        return JsonResponse({
            'success': False, 
            'message': 'Failed to resend OTP. Please try again.'
        }, status=500)

# ==============================================================================
# PASSWORD RESET FUNCTIONALITY - Added by AI Assistant on 2025-01-14
# ==============================================================================

def send_password_reset_code(request):
    """
    Send OTP code for password reset via email or SMS.
    """
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        recovery_method = data.get('recovery_method', 'email')
        contact_value = data.get('contact_value', '').strip()
        
        if not contact_value:
            return JsonResponse({
                'success': False, 
                'message': 'Please provide email or phone number'
            }, status=400)
        
        # Find user by email or phone
        user = None
        phone = None
        email = None
        
        if recovery_method == 'email':
            email = contact_value.lower()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'No account found with this email address'
                }, status=404)
        else:  # phone
            phone = contact_value
            try:
                profile = UserProfile.objects.get(phone=phone)
                user = profile.user
                email = user.email
            except UserProfile.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'No account found with this phone number'
                }, status=404)
        
        # Get phone number if we don't have it
        if not phone and user:
            try:
                profile = UserProfile.objects.get(user=user)
                phone = profile.phone
            except UserProfile.DoesNotExist:
                pass
        
        # Delete any existing unverified password reset OTPs
        OTP.objects.filter(email=email, purpose='password_reset', is_verified=False).delete()
        
        # Generate new OTP
        otp = OTP.objects.create(email=email, purpose='password_reset')
        
        # Store email in session for later steps
        request.session['reset_email'] = email
        
        # Send OTP
        if recovery_method == 'email' or not phone:
            # Send via email only
            send_mail(email, otp.code)
        else:
            # Send via both email and SMS
            send_otp(email, phone, otp.code)
        
        return JsonResponse({
            'success': True, 
            'message': 'Verification code sent successfully',
            'contact_masked': mask_contact(contact_value, recovery_method)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error in send_password_reset_code: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Failed to send verification code. Please try again.'
        }, status=500)

def verify_password_reset_code(request):
    """
    Verify the OTP code for password reset.
    """
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        
        if not code or len(code) != 6:
            return JsonResponse({
                'success': False, 
                'message': 'Please enter a valid 6-digit code'
            }, status=400)
        
        # Get email from session
        email = request.session.get('reset_email')
        if not email:
            return JsonResponse({
                'success': False, 
                'message': 'Session expired. Please start over.'
            }, status=400)
        
        # Verify OTP
        try:
            otp = OTP.objects.get(
                email=email, 
                code=code, 
                purpose='password_reset', 
                is_verified=False
            )
            
            if otp.is_expired():
                return JsonResponse({
                    'success': False, 
                    'message': 'Verification code has expired. Please request a new one.'
                }, status=400)
            
            # Mark OTP as verified but don't delete it yet
            otp.is_verified = True
            otp.save()
            
            # Store verification status in session
            request.session['reset_code_verified'] = True
            
            return JsonResponse({
                'success': True, 
                'message': 'Code verified successfully'
            })
            
        except OTP.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid verification code'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error in verify_password_reset_code: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Failed to verify code. Please try again.'
        }, status=500)

def reset_password(request):
    """
    Reset user password after OTP verification.
    """
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validate passwords
        if not new_password or not confirm_password:
            return JsonResponse({
                'success': False, 
                'message': 'Please provide both passwords'
            }, status=400)
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False, 
                'message': 'Passwords do not match'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False, 
                'message': 'Password must be at least 8 characters long'
            }, status=400)
        
        # Check session
        email = request.session.get('reset_email')
        code_verified = request.session.get('reset_code_verified')
        
        if not email or not code_verified:
            return JsonResponse({
                'success': False, 
                'message': 'Session expired or invalid. Please start over.'
            }, status=400)
        
        # Get user and update password
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clean up session
            request.session.pop('reset_email', None)
            request.session.pop('reset_code_verified', None)
            
            # Delete used OTPs
            OTP.objects.filter(email=email, purpose='password_reset').delete()
            
            return JsonResponse({
                'success': True, 
                'message': 'Password reset successfully'
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'User not found'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Failed to reset password. Please try again.'
        }, status=500)

def resend_password_reset_code(request):
    """
    Resend OTP for password reset.
    """
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    try:
        # Get email from session
        email = request.session.get('reset_email')
        if not email:
            return JsonResponse({
                'success': False, 
                'message': 'Session expired. Please start over.'
            }, status=400)
        
        # Get user and phone
        user = User.objects.get(email=email)
        phone = None
        try:
            profile = UserProfile.objects.get(user=user)
            phone = profile.phone
        except UserProfile.DoesNotExist:
            pass
        
        # Delete old OTPs
        OTP.objects.filter(email=email, purpose='password_reset', is_verified=False).delete()
        
        # Generate new OTP
        otp = OTP.objects.create(email=email, purpose='password_reset')
        
        # Send OTP
        if phone:
            send_otp(email, phone, otp.code)
        else:
            send_mail(email, otp.code)
        
        return JsonResponse({
            'success': True, 
            'message': 'Verification code resent successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        print(f"Error in resend_password_reset_code: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Failed to resend code. Please try again.'
        }, status=500)

def mask_contact(contact, method):
    """
    Mask email or phone number for privacy.
    """
    if method == 'email':
        parts = contact.split('@')
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            if len(username) > 3:
                masked = username[:2] + '*' * (len(username) - 3) + username[-1]
            else:
                masked = username[0] + '*' * (len(username) - 1)
            return f"{masked}@{domain}"
    else:  # phone
        if len(contact) > 6:
            return contact[:3] + '*' * (len(contact) - 6) + contact[-3:]
    return contact


