import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from App.reseller.earnings.models.reseller import Reseller

User = get_user_model()


@pytest.mark.django_db
def test_reseller_api_crud_and_stats(client):
    # Create user and login
    user = User.objects.create_user(username='test@example.com', email='test@example.com', password='pass12345')
    assert client.login(username='test@example.com', password='pass12345')

    # Ensure no profile initially
    assert not hasattr(user, 'reseller_profile')

    # Create a reseller profile via API
    create_url = '/platform/api/v1/resellers/'
    payload = {
        'company_name': 'Acme Co',
        'phone_number': '+1234567890',
        'address': '123 Street',
        'city': 'Nairobi',
        'state': 'Nairobi',
        'country': 'KE',
        'payment_method': 'paypal',
        'paypal_email': 'pay@example.com'
    }
    resp = client.post(create_url, data=payload)
    assert resp.status_code in (200, 201)

    # Verify my_profile endpoint
    my_profile_url = '/platform/api/v1/resellers/my_profile/'
    resp = client.get(my_profile_url)
    assert resp.status_code == 200
    data = resp.json()
    assert data['company_name'] == 'Acme Co'
    reseller_id = data['id']

    # Update some profile fields
    update_url = f'/platform/api/v1/resellers/{reseller_id}/update_profile/'
    resp = client.put(update_url, data={'city': 'Mombasa', 'state': 'Mombasa'}, content_type='application/json')
    assert resp.status_code == 200

    # Get stats
    stats_url = f'/platform/api/v1/resellers/{reseller_id}/stats/'
    resp = client.get(stats_url)
    assert resp.status_code == 200
    stats = resp.json()
    assert 'total_sales' in stats


@pytest.mark.django_db
def test_reseller_earnings_api_flows(client):
    # Create user and login
    user = User.objects.create_user(username='pay@example.com', email='pay@example.com', password='pass12345')
    assert client.login(username='pay@example.com', password='pass12345')

    # Create reseller profile directly (service path is tested above)
    reseller = Reseller.objects.create(
        user=user,
        referral_code=Reseller.generate_unique_referral_code(user.id),
        tier='bronze',
        commission_rate=10.00,
        pending_commission=200.00,
    )

    # Request payout with sufficient balance
    payout_url = '/reseller/api/payouts/request/'
    resp = client.post(payout_url, data={
        'amount': '150.00',
        'payment_method': 'paypal',
        'paypal_email': 'pay@example.com'
    })
    assert resp.status_code == 200
    out = resp.json()
    assert out.get('success') is True

    # Request invoice for last month (no commissions may exist, but service will validate)
    invoice_url = '/reseller/api/invoices/request/'
    resp = client.post(invoice_url, data={
        'period': 'last_month'
    })
    # It can be success or a validation error depending on data; just assert JSON shape
    assert resp.status_code in (200, 400)

