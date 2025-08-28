from django.test import TestCase, Client
from django.urls import reverse
from App.models import Business


class BusinessAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.b1 = Business.objects.create(
            business_name="TechCorp Solutions",
            business_email="contact@techcorp.com",
            industry="Information Technology",
            company_size="51-200",
            country="Kenya",
            postal_code="00100",
        )
        self.b2 = Business.objects.create(
            business_name="RetailHub",
            business_email="hello@retailhub.com",
            industry="Retail",
            company_size="11-50",
            country="Kenya",
            postal_code="20100",
        )

    def test_list_businesses_endpoint(self):
        url = reverse('api_businesses_list')
        res = self.client.get(url, {'q': 'retail'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['id'], self.b2.id)

    def test_business_detail_endpoint(self):
        url = reverse('api_businesses_detail', kwargs={'pk': self.b1.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['id'], self.b1.id)
        self.assertIn('postal_code', data)

    def test_business_detail_404(self):
        url = reverse('api_businesses_detail', kwargs={'pk': 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

