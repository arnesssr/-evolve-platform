from ..models.billing import Payment, Invoice
from django.utils import timezone
import uuid

class BillingRepository:
    @staticmethod
    def create_invoice(subscription, amount, due_date):
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        return Invoice.objects.create(
            subscription=subscription,
            invoice_number=invoice_number,
            amount=amount,
            due_date=due_date
        )
    
    @staticmethod
    def create_payment(subscription, amount, payment_method):
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        return Payment.objects.create(
            subscription=subscription,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id
        )
    
    @staticmethod
    def get_pending_invoices(business):
        return Invoice.objects.filter(
            subscription__business=business,
            is_paid=False,
            due_date__gte=timezone.now()
        )