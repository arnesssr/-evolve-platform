from django import forms

class ResellerFilterForm(forms.Form):
    q = forms.CharField(required=False)
    performance = forms.ChoiceField(required=False, choices=[
        ('', 'All'), ('top', 'Top'), ('good', 'Good'), ('average', 'Average'), ('poor', 'Needs Improvement')
    ])
    commission_tier = forms.ChoiceField(required=False, choices=[
        ('', 'All'), ('premium', 'Premium'), ('standard', 'Standard'), ('basic', 'Basic')
    ])
    status = forms.ChoiceField(required=False, choices=[
        ('', 'All'), ('active', 'Active'), ('suspended', 'Suspended'), ('pending', 'Pending')
    ])
    joined_from = forms.DateField(required=False)
    joined_to = forms.DateField(required=False)
    page = forms.IntegerField(required=False, min_value=1)
    page_size = forms.IntegerField(required=False, min_value=1, max_value=200)

class ResellerCreateForm(forms.Form):
    # Either provide an existing user_id OR provide new user details (email + first/last name)
    user_id = forms.IntegerField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    company = forms.CharField(required=False)
    tier = forms.ChoiceField(choices=[('basic','Basic'),('standard','Standard'),('premium','Premium')])
    territory = forms.CharField(required=False)
    specialization = forms.CharField(required=False)
    status = forms.ChoiceField(choices=[('active','Active'),('suspended','Suspended'),('pending','Pending')], initial='active')

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('user_id'):
            # Require email if creating a new user
            if not cleaned.get('email'):
                raise forms.ValidationError('Provide user_id of an existing user or specify email to create a user.')
        return cleaned

class ResellerEditForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    company = forms.CharField(required=False)
    tier = forms.ChoiceField(required=False, choices=[('basic','Basic'),('standard','Standard'),('premium','Premium')])
    territory = forms.CharField(required=False)
    specialization = forms.CharField(required=False)
    status = forms.ChoiceField(required=False, choices=[('active','Active'),('suspended','Suspended'),('pending','Pending')])

class ResellerBulkActionForm(forms.Form):
    action = forms.ChoiceField(choices=[('suspend','Suspend'),('resume','Resume'),('delete','Delete'),('set_tier','Set Tier'),('message','Message')])
    reseller_ids = forms.CharField()  # comma-separated IDs from UI
    tier = forms.ChoiceField(required=False, choices=[('basic','Basic'),('standard','Standard'),('premium','Premium')])
    message = forms.CharField(required=False)

class SuspendForm(forms.Form):
    reason = forms.CharField()
    description = forms.CharField(required=False)
    durationType = forms.ChoiceField(choices=[('temporary','Temporary'),('permanent','Permanent')], required=False)
    suspensionDuration = forms.IntegerField(required=False)
    endDate = forms.DateField(required=False)
    blockLogin = forms.BooleanField(required=False)
    freezeCommissions = forms.BooleanField(required=False)
    blockPayouts = forms.BooleanField(required=False)
    notifyUser = forms.BooleanField(required=False)

class PayoutForm(forms.Form):
    amount = forms.DecimalField(required=False, max_digits=12, decimal_places=2)
    period = forms.CharField(required=False)
    payment_method = forms.ChoiceField(required=False, choices=[('bank_transfer','Bank Transfer'),('paypal','PayPal'),('check','Check')])
    schedule = forms.ChoiceField(required=False, choices=[('immediate','Immediate'),('scheduled','Scheduled')])
    scheduled_date = forms.DateField(required=False)
    scheduled_time = forms.TimeField(required=False)
    notes = forms.CharField(required=False)

class MessageForm(forms.Form):
    reseller_ids = forms.CharField()  # comma-separated IDs
    channel = forms.ChoiceField(choices=[('email','Email'),('sms','SMS')])
    subject = forms.CharField(required=False)
    body = forms.CharField()

