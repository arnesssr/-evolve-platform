from ..repositories.billing_repository import BillingRepository
from django.utils import timezone
from datetime import timedelta

class BillingService:
    def __init__(self):
        self.repository = BillingRepository()
    
    def initiate_payment(self, subscription, amount, payment_method):
        # Create invoice first
        due_date = timezone.now() + timedelta(days=7)
        invoice = self.repository.create_invoice(subscription, amount, due_date)
        
        # Create payment record
        payment = self.repository.create_payment(subscription, amount, payment_method)
        
        # Update invoice with payment reference
        invoice.payment = payment
        invoice.save()
        
        return {
            'invoice': invoice,
            'payment': payment
        }
    
    def process_mpesa_payment(self, phone_number, amount, account_ref):
        # Implement M-Pesa integration here
        pass