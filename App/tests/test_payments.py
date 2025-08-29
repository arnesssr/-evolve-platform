from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User
from decimal import Decimal
from App.models import UserProfile, Plan, Subscription, PaymentRecord
from App.reseller.earnings.models.reseller import Reseller
from App.reseller.marketing.models import MarketingLink
from App.reseller.earnings.models import Commission


class PaymentsIPNTests(TestCase):
    def setUp(self):
        # Business user
        self.user = User.objects.create_user(
            username='biz@example.com', email='biz@example.com', password='Passw0rd!'
        )
        UserProfile.objects.create(user=self.user, phone='0712345678', role='business_owner')

        # Active plan
        self.plan = Plan.objects.create(
            name='Standard', badge='', description='Std', price=Decimal('5000.00'), yearly_price=Decimal('50000.00'), is_active=True, display_order=1
        )

        # Reseller + marketing link
        self.reseller_user = User.objects.create_user(
            username='reseller@example.com', email='reseller@example.com', password='Passw0rd!'
        )
        self.reseller = Reseller.objects.create(
            user=self.reseller_user,
            referral_code='REF123',
            tier='bronze',
            commission_rate=Decimal('10.00'),
            is_active=True,
        )
        self.link = MarketingLink.objects.create(
            reseller=self.reseller,
            title='Payroll Promo',
            code='ABC123',
            destination_url='/',
            clicks=0,
            is_active=True,
        )

        self.client = Client()
        self.client.force_login(self.user)

    def test_ipn_completed_activates_subscription_and_creates_commission(self):
        # Simulate click attribution
        resp = self.client.get(reverse('link_redirect', kwargs={'code': 'ABC123'}), follow=True)
        self.assertEqual(resp.status_code, 200)
        # Create initiated payment with affiliate marker in description
        merchant_ref = f"U{self.user.id}-TESTREF"
        PaymentRecord.objects.create(
            user=self.user,
            order_id=merchant_ref,
            amount=Decimal('5000.00'),
            currency='KES',
            description='Payroll System - Monthly Plan (Standard) | AFF=ABC123',
            phone_number='0712345678',
            status='initiated'
        )

        # Call IPN with COMPLETED status
        with patch('App.integrations.pesapal_service.get_transaction_status') as mock_status:
            mock_status.return_value = 'COMPLETED'
            r = self.client.get(reverse('ipn_listener'), {
                'order_tracking_id': 'TRACK123',
                'order_merchant_reference': merchant_ref,
            })
            self.assertEqual(r.status_code, 200)

        # PaymentRecord should be completed
        pr = PaymentRecord.objects.get(order_id=merchant_ref)
        self.assertEqual(pr.status, 'completed')
        self.assertEqual(pr.provider_tracking_id, 'TRACK123')

        # Subscription should be active
        sub = Subscription.objects.filter(user=self.user, product='payroll').first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.status, 'active')

        # Commission should be created for reseller
        self.assertTrue(Commission.objects.filter(transaction_reference='TRACK123').exists())

        # Launch gating should now allow redirect to software
        r2 = self.client.get(reverse('launch-payroll'))
        self.assertEqual(r2.status_code, 302)
        self.assertIn('/software/payroll/', r2['Location'])

    def test_payment_confirm_does_not_duplicate_commission(self):
        # Pre-create completed payment and commission via IPN path
        merchant_ref = f"U{self.user.id}-TEST2"
        PaymentRecord.objects.create(
            user=self.user,
            order_id=merchant_ref,
            amount=Decimal('5000.00'),
            currency='KES',
            description='Payroll System - Monthly Plan (Standard) | AFF=ABC123',
            phone_number='0712345678',
            status='initiated'
        )
        with patch('App.integrations.pesapal_service.get_transaction_status') as mock_status:
            mock_status.return_value = 'COMPLETED'
            self.client.get(reverse('ipn_listener'), {
                'order_tracking_id': 'TRACKX',
                'order_merchant_reference': merchant_ref,
            })

        self.assertTrue(Commission.objects.filter(transaction_reference='TRACKX').exists())
        initial_commissions = Commission.objects.count()

        # Now call payment_confirm for the same transaction
        with patch('App.integrations.pesapal_service.get_transaction_status') as mock_status2:
            mock_status2.return_value = 'COMPLETED'
            r = self.client.get(
                reverse('payment_confirm') + f"?order_tracking_id=TRACKX&order_merchant_reference={merchant_ref}"
            )
            # Redirect back to dashboard
            self.assertEqual(r.status_code, 302)

        # Ensure no duplicate commission created
        self.assertEqual(Commission.objects.count(), initial_commissions)

