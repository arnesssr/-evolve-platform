from django import forms
from App.models import Business


class BusinessCreateForm(forms.Form):
    business_name = forms.CharField(max_length=100)
    business_email = forms.EmailField()
    industry = forms.CharField(max_length=50)
    company_size = forms.CharField(max_length=20)
    country = forms.CharField(max_length=50)
    postal_code = forms.CharField(max_length=20)

    def clean_industry(self):
        value = self.cleaned_data.get('industry')
        valid = [c[0] for c in Business.INDUSTRY_CHOICES]
        if value not in valid:
            raise forms.ValidationError("Invalid industry")
        return value

    def clean_company_size(self):
        value = self.cleaned_data.get('company_size')
        valid = [c[0] for c in Business.COMPANY_SIZE_CHOICES]
        if value not in valid:
            raise forms.ValidationError("Invalid company size")
        return value

    def clean_country(self):
        value = self.cleaned_data.get('country')
        valid = [c[0] for c in Business.COUNTRY_CHOICES]
        if value not in valid:
            raise forms.ValidationError("Invalid country")
        return value

    def clean_business_email(self):
        value = self.cleaned_data.get('business_email')
        if Business.objects.filter(business_email__iexact=value).exists():
            raise forms.ValidationError("A business with this email already exists")
        return value

