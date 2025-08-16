# Reseller Views

This directory contains Django view functions that handle HTTP requests and responses for the reseller module. These views follow the traditional Django pattern for server-side rendering.

## View Components

### 1. Profile Views (`profile_views.py`) 🆕
Manages all reseller profile-related pages and operations.

**Key Views:**

#### `profile_view(request)`
- Displays the reseller's complete profile
- Shows profile statistics and completion status
- Redirects to setup if no profile exists

#### `profile_edit(request)`
- Allows resellers to edit their profile information
- Uses `ResellerProfileForm` for validation
- Displays success messages on update

#### `payment_method_update(request)`
- Dedicated view for updating payment methods
- Conditional form fields based on payment type
- Secure handling of financial information

#### `profile_setup(request)`
- Initial profile setup wizard for new resellers
- Creates reseller profile using `ResellerService`
- Redirects existing resellers to their profile

#### `profile_verification(request)`
- Handles verification requests
- Document upload support
- Checks if already verified

#### `profile_completion_status(request)`
- AJAX endpoint for profile completion percentage
- Returns JSON response
- Used for dynamic UI updates

#### `profile_stats(request)`
- Displays detailed profile statistics
- Shows recent commission history
- Performance metrics visualization

#### `deactivate_profile(request)`
- Handles profile deactivation requests
- Requires POST confirmation
- Redirects to home after deactivation

## URL Patterns

Views should be included in URL patterns like:

```python
from myapp.reseller.views import profile_views

urlpatterns = [
    path('profile/', profile_views.profile_view, name='profile_view'),
    path('profile/edit/', profile_views.profile_edit, name='profile_edit'),
    path('profile/payment-method/', profile_views.payment_method_update, name='payment_method_update'),
    path('profile/setup/', profile_views.profile_setup, name='profile_setup'),
    path('profile/verify/', profile_views.profile_verification, name='profile_verification'),
    path('profile/completion-status/', profile_views.profile_completion_status, name='profile_completion_status'),
    path('profile/stats/', profile_views.profile_stats, name='profile_stats'),
    path('profile/deactivate/', profile_views.deactivate_profile, name='deactivate_profile'),
]
```

## Template Requirements

These views expect the following templates:
- `dashboards/reseller/pages/profile/view_profile.html`
- `dashboards/reseller/pages/profile/edit_profile.html`
- `dashboards/reseller/pages/profile/payment_method.html`
- `dashboards/reseller/pages/profile/profile_wizard.html`
- `dashboards/reseller/pages/profile/profile_verification.html`
- `dashboards/reseller/pages/profile/profile_stats.html`
- `dashboards/reseller/pages/profile/deactivate_confirm.html`

## Security

- All views require authentication (`@login_required`)
- Profile access is restricted to the owner
- CSRF protection on all POST requests
- Secure handling of payment information

## Integration

These views work with:
- **Services**: Use `ResellerService` for business logic
- **Forms**: Utilize profile forms for validation
- **Models**: Access reseller profile data
- **Templates**: Render HTML responses

## Future Enhancements

1. **Two-Factor Authentication**: Add 2FA for profile changes
2. **Activity Logging**: Track all profile modifications
3. **Email Notifications**: Send emails on profile updates
4. **Bulk Operations**: Admin views for managing multiple profiles
