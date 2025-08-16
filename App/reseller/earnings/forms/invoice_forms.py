"""Invoice forms."""
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, date


class InvoiceRequestForm(forms.Form):
    """Form for requesting an invoice."""
    period = forms.ChoiceField(
        choices=[
            ('last_month', 'Last Month'),
            ('current_month', 'Current Month'),
            ('custom', 'Custom Range'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'period-select'
        })
    )
    
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes or description'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        period = cleaned_data.get('period')
        
        if period == 'custom':
            from_date = cleaned_data.get('from_date')
            to_date = cleaned_data.get('to_date')
            
            if not from_date:
                raise ValidationError('From date is required for custom period.')
            if not to_date:
                raise ValidationError('To date is required for custom period.')
            
            if from_date > to_date:
                raise ValidationError('From date cannot be after to date.')
            
            if to_date > date.today():
                raise ValidationError('To date cannot be in the future.')
        
        return cleaned_data
