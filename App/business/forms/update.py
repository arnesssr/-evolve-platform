from django import forms
from App.models import Business


class BusinessUpdateForm(forms.Form):
    business_name = forms.CharField(max_length=100, required=False)
    business_email = forms.EmailField(required=False)
    industry = forms.CharField(max_length=50, required=False)
    company_size = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=50, required=False)
    postal_code = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, instance: Business | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean_industry(self):
        value = self.cleaned_data.get('industry')
        if value is None or value == '':
            return value
        valid = [c[0] for c in Business.INDUSTRY_CHOICES]
        if value not in valid:
            raise forms.ValidationError("Invalid industry")
        return value

    def clean_company_size(self):
        value = self.cleaned_data.get('company_size')
        if value is None or value == '':
            return value
        valid = [c[0] for c in Business.COMPANY_SIZE_CHOICES]
        if value not in valid:
            raise forms.ValidationError("Invalid company size")
        return value

    def clean_country(self):
        value = self.cleaned_data.get('country')
        if value is None or value == '':
            return value
        valid = [c[0] for c in Business.COUNTRY_CHOICES]
        if value not in valid:
            raise forms.ValidationError("Invalid country")
        return value

    def clean_business_email(self):
        value = self.cleaned_data.get('business_email')
        if value in (None, ''):
            return value
        qs = Business.objects.filter(business_email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A business with this email already exists")
        return value

