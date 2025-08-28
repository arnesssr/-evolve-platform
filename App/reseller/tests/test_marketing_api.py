import pytest
from django.contrib.auth.models import User
from App.reseller.earnings.models.reseller import Reseller

@pytest.mark.django_db
def test_marketing_api_links_tools_resources(client):
    # Create user and profile
    user = User.objects.create_user(username='mkt@example.com', email='mkt@example.com', password='pass12345')
    assert client.login(username='mkt@example.com', password='pass12345')

    reseller = Reseller.objects.create(
        user=user,
        referral_code=Reseller.generate_unique_referral_code(user.id),
    )

    # Create a marketing link
    payload = {
        'title': 'Homepage Link',
        'code': 'HOME123',
        'destination_url': 'https://example.com',
        'is_active': True,
    }
    resp = client.post('/platform/api/v1/marketing/links/', data=payload)
    assert resp.status_code in (200, 201), resp.content

    # List links
    resp = client.get('/platform/api/v1/marketing/links/')
    assert resp.status_code == 200

    # Tools and resources (empty lists by default)
    resp = client.get('/platform/api/v1/marketing/tools/')
    assert resp.status_code == 200
    resp = client.get('/platform/api/v1/marketing/resources/')
    assert resp.status_code == 200

