import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from App.reseller.earnings.models.reseller import Reseller
from App.reseller.earnings.models.invoice import Invoice
from App.reseller.earnings.models.commission import Commission
from App.reseller.earnings.models.payout import Payout
from App.reseller.earnings.models.base import InvoiceStatusChoices, PayoutStatusChoices, CommissionStatusChoices


class FinanceApiIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create staff user
        self.user = User.objects.create_user(username='admin', email='admin@example.com', password='pass')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

        # Create reseller and sample data
        self.res_user = User.objects.create_user(username='reseller', email='reseller@example.com', password='pass')
        self.reseller = Reseller.objects.create(user=self.res_user, referral_code='REF123', company_name='Acme Co')

        today = datetime.date.today()
        # Invoice (paid)
        self.invoice = Invoice.objects.create(
            reseller=self.reseller,
            period_start=today - datetime.timedelta(days=30),
            period_end=today,
            description='Monthly invoice',
            subtotal=100,
            tax_amount=0,
            total_amount=100,
            status=InvoiceStatusChoices.PAID,
            issue_date=today - datetime.timedelta(days=15),
            due_date=today - datetime.timedelta(days=5),
            payment_date=today - datetime.timedelta(days=3),
        )

        # Commission (approved)
        self.commission = Commission.objects.create(
            reseller=self.reseller,
            transaction_reference='TXN123',
            client_name='Client A',
            product_name='Product X',
            sale_amount=500,
            amount=50,
            commission_rate=10,
            status=CommissionStatusChoices.APPROVED,
        )

        # Payout (completed)
        self.payout = Payout.objects.create(
            reseller=self.reseller,
            amount=25,
            payment_method='bank_transfer',
            status=PayoutStatusChoices.COMPLETED,
        )
        # Set completion date explicitly for clarity
        self.payout.complete_payout(transaction_reference='TRX-1')

    def test_revenue_endpoints(self):
        # Trends
        r = self.client.get('/platform/admin/api/v1/finance/revenue/trends/?interval=monthly')
        if r.status_code != 200:
            print('Revenue trends error:', r.content)
        self.assertEqual(r.status_code, 200)
        data = r.json()['data']
        self.assertIn('trends', data)

        # Source breakdown
        r = self.client.get('/platform/admin/api/v1/finance/revenue/source-breakdown/')
        self.assertEqual(r.status_code, 200)
        data = r.json()['data']
        self.assertIn('sources', data)

    def test_invoices_list(self):
        r = self.client.get('/platform/admin/api/v1/finance/invoices/?page_size=50')
        self.assertEqual(r.status_code, 200)
        payload = r.json()['data']
        self.assertTrue(len(payload['invoices']) >= 1)
        inv = payload['invoices'][0]
        self.assertIn('invoice_number', inv)
        self.assertIn('amount', inv)

    def test_payouts_list(self):
        r = self.client.get('/platform/admin/api/v1/finance/payouts/?page_size=50')
        self.assertEqual(r.status_code, 200)
        payload = r.json()['data']
        self.assertTrue(len(payload['payouts']) >= 1)
        po = payload['payouts'][0]
        self.assertIn('amount', po)
        self.assertIn('method', po)

    def test_commissions_list(self):
        r = self.client.get('/platform/admin/api/v1/finance/commissions/?page_size=50')
        if r.status_code != 200:
            print('Commissions list error:', r.content)
        self.assertEqual(r.status_code, 200)
        payload = r.json()['data']
        self.assertTrue(len(payload['commissions']) >= 1)
        cm = payload['commissions'][0]
        self.assertIn('amount', cm)
        self.assertIn('status', cm)

    def test_transactions_list(self):
        r = self.client.get('/platform/admin/api/v1/finance/transactions/?page_size=200')
        self.assertEqual(r.status_code, 200)
        payload = r.json()['data']
        self.assertTrue('transactions' in payload)
        self.assertTrue(payload['pagination']['total_count'] >= 1)

