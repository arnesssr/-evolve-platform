import pytest
from django.contrib.auth import get_user_model
from App.reseller.earnings.models.reseller import Reseller

User = get_user_model()


@pytest.mark.django_db
def test_reseller_pages_render(client):
    # Create user and login
    user = User.objects.create_user(username='pages@example.com', email='pages@example.com', password='pass12345')
    assert client.login(username='pages@example.com', password='pass12345')

    # Create reseller profile
    Reseller.objects.create(
        user=user,
        referral_code=Reseller.generate_unique_referral_code(user.id),
        tier='bronze',
        commission_rate=10.00,
        pending_commission=0,
    )

    # Pages to check
    urls = [
        '/reseller/',
        '/reseller/commissions/',
        '/reseller/invoices/',
        '/reseller/payouts/',
        '/reseller/profile/',
        '/reseller/profile/edit/',
        '/reseller/profile/payment-method/',
        '/reseller/profile/setup/',
        '/reseller/profile/verify/',
        '/reseller/profile/stats/',
        '/reseller/links/',
        '/reseller/tools/',
        '/reseller/resources/',
        '/reseller/settings/',
    ]

    for url in urls:
        resp = client.get(url)
        # Some flows (setup) may redirect if profile exists; accept 200 or redirect
        assert resp.status_code in (200, 302)

