from django.test import TestCase, Client
from django.contrib.auth.models import User

class SettingsUiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='pass')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

    def test_general_settings_contains_kes(self):
        r = self.client.get('/platform/admin/settings/general/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('KES - Kenyan Shilling', r.content.decode())

