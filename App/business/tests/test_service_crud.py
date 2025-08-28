from django.test import TestCase
from App.business.services.business_service import BusinessService
from App.models import Business


class BusinessServiceCrudTests(TestCase):
    def setUp(self):
        self.svc = BusinessService()

    def test_create_update_delete(self):
        created = self.svc.create_business({
            'business_name': 'MegaCorp',
            'business_email': 'contact@megacorp.com',
            'industry': 'Manufacturing',
            'company_size': '51-200',
            'country': 'Kenya',
            'postal_code': '11111',
        })
        self.assertIn('id', created)
        self.assertEqual(created['email'], 'contact@megacorp.com')

        updated = self.svc.update_business(created['id'], {'company_size': '200+'})
        self.assertEqual(updated['company_size'], '200+')

        self.svc.delete_business(created['id'])
        self.assertEqual(Business.objects.filter(pk=created['id']).count(), 0)

