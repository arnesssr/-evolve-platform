from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class AdminResellersViewsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', email='admin@example.com', password='pass', is_staff=True)
        self.client = Client()
        self.client.login(username='admin', password='pass')

    def test_resellers_list_page(self):
        url = reverse('platform_admin:resellers-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_api_list(self):
        url = reverse('platform_admin:platform_admin_api_v1:resellers-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

