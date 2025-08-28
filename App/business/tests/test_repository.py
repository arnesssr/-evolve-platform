from django.test import TestCase
from App.business.repositories.business_repository import BusinessRepository
from App.models import Business


class BusinessRepositoryTests(TestCase):
    def setUp(self):
        Business.objects.create(
            business_name="TechCorp Solutions",
            business_email="contact@techcorp.com",
            industry="Information Technology",
            company_size="51-200",
            country="Kenya",
            postal_code="00100",
        )
        Business.objects.create(
            business_name="RetailHub",
            business_email="hello@retailhub.com",
            industry="Retail",
            company_size="11-50",
            country="Kenya",
            postal_code="20100",
        )
        Business.objects.create(
            business_name="AgriCo",
            business_email="info@agrico.com",
            industry="Agriculture",
            company_size="1-10",
            country="Kenya",
            postal_code="30100",
        )

    def test_search_by_q_matches_name_or_email(self):
        repo = BusinessRepository()
        qs = repo.search(q="tech")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().business_name, "TechCorp Solutions")

        qs2 = repo.search(q="retailhub.com")
        self.assertEqual(qs2.count(), 1)
        self.assertEqual(qs2.first().business_name, "RetailHub")

    def test_filter_by_industry(self):
        repo = BusinessRepository()
        qs = repo.search(industry="Retail")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().industry, "Retail")

