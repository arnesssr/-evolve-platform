from django.test import TestCase
from App.business.repositories.business_repository import BusinessRepository
from App.models import Business


class BusinessRepositoryCrudTests(TestCase):
    def setUp(self):
        self.repo = BusinessRepository()

    def test_create_update_delete(self):
        b = self.repo.create({
            'business_name': 'NewCo',
            'business_email': 'new@co.com',
            'industry': 'Retail',
            'company_size': '1-10',
            'country': 'Kenya',
            'postal_code': '00100',
        })
        self.assertIsNotNone(b.id)
        self.assertEqual(b.business_email, 'new@co.com')

        b2 = self.repo.update(b, {'business_name': 'NewCo Limited', 'company_size': '11-50'})
        self.assertEqual(b2.business_name, 'NewCo Limited')
        self.assertEqual(b2.company_size, '11-50')

        self.repo.delete(b2.id)
        self.assertEqual(Business.objects.filter(pk=b2.id).count(), 0)

