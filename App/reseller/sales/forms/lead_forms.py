"""Sales forms."""
from django import forms
from ..models.lead import Lead
from ..models.referral import Referral


class LeadCreateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'phone', 'company', 'source', 'notes']


class ReferralCreateForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = ['referred_name', 'referred_email', 'referred_phone', 'referral_code_used', 'notes']

