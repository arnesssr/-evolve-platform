# Template Folder Structure

This directory contains all the Django templates for the Evolve Payments Platform, organized in a scalable folder structure.

## Folder Organization

```
templates/
├── auth/                      # Authentication related templates
│   ├── login.html            # User login page
│   ├── register.html         # User registration page
│   ├── forgot-password.html  # Password recovery page
│   └── verify_otp.html       # OTP verification page
│
├── dashboards/               # All dashboard templates by role
│   ├── admin/
│   │   ├── admin-dashboard-test.html  # Admin dashboard
│   │   └── edit-plans.html           # Admin plan management
│   ├── business/
│   │   └── business-dashboard.html   # Business owner dashboard
│   └── reseller/
│       └── reseller-dashboard.html   # Reseller dashboard
│
├── onboarding/               # User onboarding flow
│   └── onboarding.html       # Business onboarding form
│
├── payments/                 # Payment related templates
│   ├── payment.html          # Payment/pricing page
│   └── payment-failed.html   # Payment failure page
│
├── emails/                   # Email templates
│   └── otp_email.html        # OTP email template
│
├── landing/                  # Public facing pages
│   └── landing.html          # Main landing page
│
└── base/                     # Base templates (for future use)
    ├── base.html             # Base template (to be created)
    └── partials/
        ├── header.html       # Common header (to be created)
        ├── footer.html       # Common footer (to be created)
        └── sidebar.html      # Common sidebar (to be created)
```

## Benefits of This Structure

1. **Scalability**: Easy to add new templates without cluttering the root directory
2. **Organization**: Templates are grouped by functionality
3. **Maintainability**: Easy to find and update related templates
4. **Separation of Concerns**: Clear separation between different parts of the application
5. **Future-Ready**: Base folder is ready for common template inheritance

## Usage

When rendering templates in Django views, use the folder path:

```python
# Examples:
return render(request, 'auth/login.html')
return render(request, 'dashboards/business/business-dashboard.html')
return render(request, 'payments/payment.html')
```

## Next Steps

1. Create `base/base.html` template for common layout inheritance
2. Extract common components (header, footer, sidebar) into partials
3. Update existing templates to extend from base template
4. Consider adding more folders as the application grows (e.g., `errors/` for error pages)
