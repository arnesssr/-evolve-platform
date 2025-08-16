"""Payout forms."""
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import Payout, PaymentMethodChoices


class PayoutRequestForm(forms.Form):
    """Form for requesting a payout."""
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('50.00'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount',
            'step': '0.01'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=PaymentMethodChoices.choices,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    bank_account_number = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank account number'
        })
    )
    
    bank_routing_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Routing number'
        })
    )
    
    paypal_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'PayPal email address'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes (optional)'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        # Validate payment method specific fields
        if payment_method == 'bank_transfer':
            if not cleaned_data.get('bank_account_number'):
                raise ValidationError('Bank account number is required for bank transfers.')
            if not cleaned_data.get('bank_routing_number'):
                raise ValidationError('Bank routing number is required for bank transfers.')
        
        elif payment_method == 'paypal':
            if not cleaned_data.get('paypal_email'):
                raise ValidationError('PayPal email is required for PayPal payouts.')
        
        return cleaned_data
