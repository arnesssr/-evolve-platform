import pytest
from django.contrib.auth.models import User
from App.reseller.earnings.models.reseller import Reseller

@pytest.mark.django_db
def test_settings_api_preferences_get_put(client):
    user = User.objects.create_user(username='set@example.com', email='set@example.com', password='pass12345')
    assert client.login(username='set@example.com', password='pass12345')

    reseller = Reseller.objects.create(
        user=user,
        referral_code=Reseller.generate_unique_referral_code(user.id),
    )

    # GET defaults
    resp = client.get('/platform/api/v1/settings/preferences/')
    assert resp.status_code == 200
    assert 'preferences' in resp.json()

    # PUT update
    new_prefs = {'notifications': {'email': True}, 'theme': 'dark'}
    resp = client.put('/platform/api/v1/settings/preferences/', data={'preferences': new_prefs}, content_type='application/json')
    assert resp.status_code == 200
    assert resp.json()['preferences']['theme'] == 'dark'

