from rest_framework import serializers
from ....models.billing import Payment, Invoice

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_method', 'transaction_id', 
                 'status', 'payment_date']

class InvoiceSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'amount', 'due_date', 
                 'is_paid', 'created_at', 'payment']