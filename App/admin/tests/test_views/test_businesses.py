from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from App.models import Business


class AdminBusinessViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='pass12345')
        self.client.login(username='admin', password='pass12345')
        self.b = Business.objects.create(
            business_name='AdminTestCo',
            business_email='admin@testco.com',
            industry='Retail',
            company_size='1-10',
            country='Kenya',
            postal_code='00100',
        )

    def test_admin_businesses_list_view_renders(self):
        url = reverse('platform_admin:businesses-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Business Customers')

    def test_admin_businesses_detail_view_renders(self):
        url = reverse('platform_admin:businesses-detail', kwargs={'user_id': self.b.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # Ensure mapped context content present
        self.assertContains(res, 'AdminTestCo')

