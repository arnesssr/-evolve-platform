from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
import json

class SettingsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='pass')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

    def test_get_and_update_general_settings(self):
        # Initial GET should succeed
        r = self.client.get('/platform/admin/api/v1/settings/general/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # Update to KES and Swahili
        payload = {
            'platform_name': 'Evolve Test',
            'default_currency': 'KES',
            'default_language': 'sw',
            'timezone': 'Africa/Nairobi',
        }
        r2 = self.client.put('/platform/admin/api/v1/settings/general/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(r2.status_code, 200, r2.content)
        updated = r2.json()
        self.assertEqual(updated.get('default_currency'), 'KES')
        self.assertEqual(updated.get('default_language'), 'sw')

    def test_security_notifications_integrations_update(self):
        r = self.client.put('/platform/admin/api/v1/settings/security/', data=json.dumps({'two_factor_enabled': True, 'password_min_length': 10}), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json().get('two_factor_enabled'))

        r2 = self.client.put('/platform/admin/api/v1/settings/notifications/', data=json.dumps({'enable_system_emails': True, 'email_sender_address': 'noreply@example.com'}), content_type='application/json')
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json().get('enable_system_emails'))

        r3 = self.client.put('/platform/admin/api/v1/settings/integrations/', data=json.dumps({'api_enabled': True}), content_type='application/json')
        self.assertEqual(r3.status_code, 200)
        self.assertTrue(r3.json().get('api_enabled'))

