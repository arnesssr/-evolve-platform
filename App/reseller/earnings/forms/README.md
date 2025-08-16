# Reseller Forms

This directory contains Django forms that handle user input and validation for the reseller module's earnings features.

## Form Components

### 1. PayoutRequestForm (`payout_forms.py`)
Handles payout requests from resellers who want to withdraw their available commissions.

**Key Features:**
- Validates minimum payout amount ($50.00)
- Supports multiple payment methods (Bank Transfer, PayPal, Stripe, Check)
- Conditional validation based on payment method
- Collects payment details (bank account, routing number, PayPal email)

**Usage:**
```python
form = PayoutRequestForm(request.POST)
if form.is_valid():
    # Process payout request
```

### 2. InvoiceRequestForm (`invoice_forms.py`)
Manages invoice generation requests for commission earnings.

**Key Features:**
- Period selection (Last Month, Current Month, Custom Range)
- Date range validation for custom periods
- Optional description field for notes
- Prevents future date selection

**Usage:**
```python
form = InvoiceRequestForm(request.POST)
if form.is_valid():
    # Generate invoice for specified period
```

### 3. ResellerProfileForm (`profile_forms.py`) 🆕
Handles reseller profile information updates.

**Key Features:**
- Company information fields (name, website, description)
- Contact details (phone, alternate email, address)
- Phone number validation (10-15 digits)
- Automatic HTTPS prepending for websites
- Bootstrap styling integration

**Usage:**
```python
form = ResellerProfileForm(request.POST, instance=reseller)
if form.is_valid():
    form.save()
```

### 4. PaymentMethodForm (`profile_forms.py`) 🆕
Manages payment method configuration for payouts.

**Key Features:**
- Multiple payment methods (Bank Transfer, PayPal, Stripe)
- Conditional field validation based on selected method
- Secure storage of payment details
- Dynamic form fields (show/hide based on payment method)

**Usage:**
```python
form = PaymentMethodForm(request.POST, instance=reseller)
if form.is_valid():
    form.save()
```

### 5. ProfileSetupWizardForm (`profile_forms.py`) 🆕
Guides new resellers through initial profile setup.

**Key Features:**
- Multi-step form structure
- Required fields for complete profile
- Payment method configuration
- Validation for all required information

**Usage:**
```python
form = ProfileSetupWizardForm(request.POST)
if form.is_valid():
    # Create new reseller profile
```

### 6. ProfileVerificationForm (`profile_forms.py`) 🆕
Handles profile verification requests.

**Key Features:**
- Business registration number collection
- Tax ID validation
- Document upload support (PDF, JPG, PNG)
- File size validation (max 5MB)
- Terms agreement checkbox

**Usage:**
```python
form = ProfileVerificationForm(request.POST, request.FILES)
if form.is_valid():
    # Process verification request
```

## Integration

These forms are used by:
- **Views**: Display forms in templates and handle submissions
- **API Views**: Process AJAX requests for seamless user experience
- **Services**: Receive validated data for business logic processing

## Benefits

1. **Data Validation**: Ensures data integrity before processing
2. **User Feedback**: Provides clear error messages
3. **Security**: Protects against invalid or malicious input
4. **Reusability**: Forms can be used in multiple views/templates
