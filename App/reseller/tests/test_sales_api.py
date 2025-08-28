import pytest
from django.contrib.auth.models import User
from App.reseller.earnings.models.reseller import Reseller

@pytest.mark.django_db
def test_sales_api_leads_referrals_and_summary(client):
    # Create user and reseller profile
    user = User.objects.create_user(username='sales@example.com', email='sales@example.com', password='pass12345')
    assert client.login(username='sales@example.com', password='pass12345')

    reseller = Reseller.objects.create(
        user=user,
        referral_code=Reseller.generate_unique_referral_code(user.id),
    )

    # Create a lead
    lead_payload = {
        'name': 'Alice Buyer',
        'email': 'alice@example.com',
        'phone': '+111111111',
        'company': 'Acme',
        'source': 'web',
        'notes': 'Hot lead',
    }
    resp = client.post('/platform/api/v1/sales/leads/', data=lead_payload)
    assert resp.status_code in (200, 201), resp.content
    lead_id = resp.json().get('id')
    assert lead_id

    # List leads
    resp = client.get('/platform/api/v1/sales/leads/')
    assert resp.status_code == 200
    data = resp.json()
    # Support both paginated and non-paginated responses
    items = data.get('results') if isinstance(data, dict) and 'results' in data else data
    assert isinstance(items, list)
    assert any(item['email'] == 'alice@example.com' for item in items)

    # Create a referral
    referral_payload = {
        'referred_name': 'Bob Prospect',
        'referred_email': 'bob@example.com',
        'referred_phone': '+222222222',
        'referral_code_used': reseller.referral_code,
        'notes': 'Interested in Pro plan',
    }
    resp = client.post('/platform/api/v1/sales/referrals/', data=referral_payload)
    assert resp.status_code in (200, 201), resp.content

    # Summary
    resp = client.get('/platform/api/v1/sales/reports/summary/')
    assert resp.status_code == 200
    summary = resp.json()
    assert 'leads_by_status' in summary
    assert 'referrals_by_status' in summary
    assert 'total_commissions' in summary

