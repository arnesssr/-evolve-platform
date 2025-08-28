from django.test import TestCase
from App.business.services.business_service import BusinessService
from App.models import Business


class BusinessServiceTests(TestCase):
    def setUp(self):
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

    def test_list_businesses_returns_paginated_payload(self):
        svc = BusinessService()
        payload = svc.list_businesses({'q': 'tech', 'page': 1, 'page_size': 25})
        self.assertIn('count', payload)
        self.assertIn('results', payload)
        self.assertEqual(payload['count'], 1)
        self.assertEqual(len(payload['results']), 1)
        self.assertEqual(payload['results'][0]['id'], self.b1.id)

    def test_get_business_returns_expected_fields(self):
        svc = BusinessService()
        data = svc.get_business(self.b2.id)
        self.assertEqual(data['id'], self.b2.id)
        self.assertEqual(data['name'], self.b2.business_name)
        self.assertIn('postal_code', data)

