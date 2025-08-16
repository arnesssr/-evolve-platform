# Reseller Profile Templates

This directory contains all the template files for reseller profile management functionality, providing a comprehensive interface for resellers to manage their business information, payment methods, and account settings.

## Why Profile Management is Needed

1. **Business Identity**: Resellers need to establish their business presence on the platform with company information, contact details, and verification status.

2. **Payment Configuration**: Before resellers can receive payouts, they must configure their preferred payment methods (bank transfer, PayPal, etc.).

3. **Trust & Verification**: Verified profiles build trust with the platform and may unlock higher commission tiers or special features.

4. **Compliance**: Collecting complete business information ensures regulatory compliance for financial transactions.

5. **Personalization**: Profile data enables personalized experiences, accurate commission calculations, and proper tier assignments.

## What It Does

The profile management system allows resellers to:
- View and edit their business information
- Configure payment methods for receiving commissions
- Track profile completion status
- Request business verification
- View detailed statistics and performance metrics
- Manage their account status (active/inactive)

## Template Files and Their Purpose

### 1. `view_profile.html`
**Purpose**: Main profile dashboard showing complete reseller information
- Displays business details, contact info, and verification status
- Shows profile completion percentage with visual progress bar
- Presents key statistics (total sales, commissions, tier status)
- Provides quick access to edit functions and payout requests

**Backend Connection**: 
- View: `profile_views.profile_view()`
- Service: `ResellerService.get_reseller_stats()`, `get_profile_completion_status()`
- Model: `Reseller` model data

### 2. `edit_profile.html`
**Purpose**: Form interface for updating profile information
- Editable fields for company name, website, description
- Contact information updates (phone, address, etc.)
- Form validation and error display

**Backend Connection**:
- View: `profile_views.profile_edit()`
- Form: `ResellerProfileForm`
- Service: `ResellerService.update_profile()`

### 3. `payment_method.html`
**Purpose**: Dedicated interface for payment method configuration
- Payment type selection (bank transfer, PayPal, Stripe)
- Dynamic form fields based on selected payment method
- Secure handling of financial information

**Backend Connection**:
- View: `profile_views.payment_method_update()`
- Form: `PaymentMethodForm`
- Validates payment-specific fields

### 4. `profile_wizard.html`
**Purpose**: Initial setup wizard for new resellers
- Step-by-step profile creation process
- Ensures all required fields are completed
- Smooth onboarding experience

**Backend Connection**:
- View: `profile_views.profile_setup()`
- Form: `ProfileSetupWizardForm`
- Service: `ResellerService.create_reseller_profile()`

### 5. `profile_verification.html`
**Purpose**: Business verification request interface
- Upload business documents (registration, tax ID)
- Verification agreement and terms acceptance
- Document validation (file type, size)

**Backend Connection**:
- View: `profile_views.profile_verification()`
- Form: `ProfileVerificationForm`
- Future: Integration with verification service

### 6. `profile_stats.html`
**Purpose**: Detailed statistics and analytics dashboard
- Comprehensive performance metrics
- Commission history and trends
- Sales performance analysis

**Backend Connection**:
- View: `profile_views.profile_stats()`
- Service: `ResellerService.get_reseller_stats()`
- Integration with `CommissionService`

### 7. `deactivate_confirm.html`
**Purpose**: Account deactivation confirmation page
- Clear warning about deactivation consequences
- Confirmation mechanism to prevent accidental deactivation
- Option to cancel and return to profile

**Backend Connection**:
- View: `profile_views.deactivate_profile()`
- Service: `ResellerService.deactivate_reseller()`

## How Templates Connect to Backend

```
User Action → Template → View Function → Service Layer → Repository → Model → Database
     ↑                                                                              ↓
     ←──────────────────── Response with Updated Data ←────────────────────────────
```

1. **URL Routing**: Each template is mapped to a specific URL pattern in `urls.py`
2. **View Functions**: Process requests and prepare context data for templates
3. **Forms**: Handle data validation and provide form widgets
4. **Services**: Execute business logic and data transformations
5. **Models**: Define data structure and relationships

## End User Expectations

### For New Resellers:
1. **Seamless Onboarding**: Quick profile setup with clear guidance
2. **Required Fields**: Clear indication of what information is mandatory
3. **Immediate Access**: Start earning commissions right after setup

### For Existing Resellers:
1. **Easy Updates**: Simple process to update business information
2. **Payment Flexibility**: Multiple payment method options
3. **Transparency**: Clear view of verification status and tier progress
4. **Performance Insights**: Detailed statistics to track success

### General Expectations:
1. **Responsive Design**: Works well on desktop and mobile devices
2. **Data Security**: Sensitive information is handled securely
3. **Validation Feedback**: Clear error messages and success confirmations
4. **Progress Tracking**: Visual indicators for profile completion
5. **Quick Actions**: Easy access to common tasks (edit, payout request)

## Integration Points

- **Navigation**: Profile menu item added to reseller dashboard sidebar
- **Dashboard Widgets**: Profile completion status on main dashboard
- **Earnings Pages**: Payment method info displayed on payout pages
- **API Endpoints**: REST API for profile operations (`/api/v1/resellers/`)

## Future Enhancements

1. **Two-Factor Authentication**: Enhanced security for profile changes
2. **Profile Images**: Business logo and avatar uploads
3. **Social Media Integration**: Link social profiles
4. **Advanced Analytics**: More detailed performance metrics
5. **Export Features**: Download profile data and statistics
