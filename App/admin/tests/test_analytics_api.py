from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from App.reseller.earnings.models.reseller import Reseller
from App.reseller.earnings.models.invoice import Invoice
from App.reseller.earnings.models.base import InvoiceStatusChoices

class AnalyticsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='pass')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

        # Seed reseller and a paid invoice for revenue trend
        res_user = User.objects.create_user(username='res', password='pass')
        self.reseller = Reseller.objects.create(user=res_user, referral_code='REFX')
        today = timezone.now().date()
        Invoice.objects.create(
            reseller=self.reseller,
            period_start=today,
            period_end=today,
            description='Test',
            subtotal=100,
            tax_amount=0,
            total_amount=100,
            status=InvoiceStatusChoices.PAID,
            issue_date=today,
            due_date=today,
            payment_date=today,
        )

    def test_growth_trends(self):
        r = self.client.get('/platform/admin/api/v1/dashboard/growth-trends/?days=7')
        if r.status_code != 200:
            # Print helpful debugging info
            try:
                print('growth-trends response body:', r.content.decode())
            except Exception:
                print('growth-trends response body: <non-decodable>')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('user_growth', data)
        self.assertIn('business_growth', data)
        self.assertIn('revenue_growth', data)

    def test_dashboard_metrics(self):
        r = self.client.get('/platform/admin/api/v1/dashboard/metrics/?period=last_7_days')
        if r.status_code != 200:
            try:
                print('dashboard-metrics response body:', r.content.decode())
            except Exception:
                print('dashboard-metrics response body: <non-decodable>')
        self.assertEqual(r.status_code, 200)
        # Basic shape checks
        self.assertIn('users', r.json())
        self.assertIn('financial', r.json())

