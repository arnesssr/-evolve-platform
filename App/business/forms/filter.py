from django import forms


class BusinessFilterForm(forms.Form):
    q = forms.CharField(required=False)
    industry = forms.CharField(required=False)
    page = forms.IntegerField(required=False, min_value=1)
    page_size = forms.IntegerField(required=False, min_value=1, max_value=500)

    # Placeholders for future fields; currently not used in repository
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
    subscription = forms.CharField(required=False)

