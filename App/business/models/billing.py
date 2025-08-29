from django.db import models
from .subscription import Subscription

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('MPESA', 'M-Pesa'),
        ('CARD', 'Credit/Debit Card'),
        ('BANK', 'Bank Transfer')
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    
class Invoice(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT)
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, null=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)