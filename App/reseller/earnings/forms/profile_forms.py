"""Forms for reseller profile management."""
from django import forms
from django.core.exceptions import ValidationError
import re

from ..models.reseller import Reseller


class ResellerProfileForm(forms.ModelForm):
    """Form for editing reseller profile information."""
    
    reseller_type = forms.ChoiceField(
        choices=[('individual', 'Individual Affiliate'), ('business', 'Business Partner')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='individual'
    )
    
    class Meta:
        model = Reseller
        fields = [
            'reseller_type', 'company_name', 'company_website', 'company_description',
            'phone_number', 'alternate_email', 'address', 'city',
            'state', 'country', 'postal_code'
        ]
        
        widgets = {
            'company_description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe your business...'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter your business address...'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Company Name'
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'alternate_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'alternate@email.com'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal/ZIP Code'
            })
        }
    
    def clean_phone_number(self):
        """Validate phone number format."""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove all non-digit characters
            cleaned_number = re.sub(r'\D', '', phone_number)
            
            # Check if it's a valid length (10-15 digits)
            if len(cleaned_number) < 10 or len(cleaned_number) > 15:
                raise ValidationError(
                    'Please enter a valid phone number with 10-15 digits.'
                )
            
            return phone_number
        return phone_number
    
    def clean_company_website(self):
        """Validate company website URL."""
        website = self.cleaned_data.get('company_website')
        if website and not website.startswith(('http://', 'https://')):
            website = f'https://{website}'
        return website
    
    def clean(self):
        """Validate fields based on reseller type."""
        cleaned_data = super().clean()
        reseller_type = cleaned_data.get('reseller_type')
        
        if reseller_type == 'business':
            # For business partners, company name is required
            if not cleaned_data.get('company_name'):
                self.add_error('company_name', 'Company name is required for business partners.')
        
        return cleaned_data


class PaymentMethodForm(forms.ModelForm):
    """Form for updating payment method information."""
    
    PAYMENT_METHOD_CHOICES = [
        ('', '-- Select Payment Method --'),
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('pesapal', 'PesaPal'),
        ('mpesa', 'M-Pesa'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Reseller
        fields = [
            'payment_method', 'bank_account_name', 'bank_account_number',
            'bank_name', 'bank_routing_number', 'paypal_email'
        ]
        
        widgets = {
            'bank_account_name': forms.TextInput(attrs={
                'class': 'form-control bank-field',
                'placeholder': 'Account Holder Name'
            }),
            'bank_account_number': forms.TextInput(attrs={
                'class': 'form-control bank-field',
                'placeholder': 'Account Number'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control bank-field',
                'placeholder': 'Bank Name'
            }),
            'bank_routing_number': forms.TextInput(attrs={
                'class': 'form-control bank-field',
                'placeholder': 'Routing Number'
            }),
            'paypal_email': forms.EmailInput(attrs={
                'class': 'form-control paypal-field',
                'placeholder': 'PayPal Email Address'
            })
        }
    
    def clean(self):
        """Validate payment method specific fields."""
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'bank':
            # Validate bank transfer fields
            required_fields = [
                'bank_account_name', 'bank_account_number', 
                'bank_name'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'{field.replace("_", " ").title()} is required for bank transfer.')
        
        elif payment_method == 'paypal':
            # Validate PayPal fields
            if not cleaned_data.get('paypal_email'):
                self.add_error('paypal_email', 'PayPal email is required for PayPal payments.')
        
        return cleaned_data


class ProfileSetupWizardForm(forms.ModelForm):
    """Form for initial profile setup wizard."""
    
    # Reseller Type Selection
    reseller_type = forms.ChoiceField(
        choices=[('individual', 'Individual Affiliate'), ('business', 'Business Partner')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='individual',
        required=True
    )
    
    # Step 1: Basic Information
    company_name = forms.CharField(
        required=False,  # Made optional, will validate in clean()
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your company name'
        })
    )
    
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    
    # Step 2: Address Information
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Enter your business address'
        })
    )
    
    city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    state = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province'
        })
    )
    
    country = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )
    
    # Step 3: Payment Information
    payment_method = forms.ChoiceField(
        required=True,
        choices=[
            ('', '-- Select Payment Method --'),
            ('bank_transfer', 'Bank Transfer'),
            ('paypal', 'PayPal'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Reseller
        fields = [
            'company_name', 'phone_number', 'address', 'city',
            'state', 'country', 'postal_code', 'payment_method',
            'bank_account_name', 'bank_account_number', 'bank_name',
            'bank_routing_number', 'paypal_email'
        ]


class ProfileVerificationForm(forms.Form):
    """Form for profile verification request."""
    
    business_registration_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Business Registration Number'
        }),
        help_text='Enter your official business registration number'
    )
    
    tax_id = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tax ID / VAT Number'
        }),
        help_text='Enter your tax identification number'
    )
    
    verification_documents = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        help_text='Upload business registration or tax documents (PDF, JPG, PNG)'
    )
    
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I certify that all information provided is accurate and complete'
    )
    
    def clean_verification_documents(self):
        """Validate uploaded documents."""
        file = self.cleaned_data.get('verification_documents')
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError('File size must not exceed 5MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            file_name = file.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise ValidationError('Only PDF, JPG, and PNG files are allowed.')
        
        return file
