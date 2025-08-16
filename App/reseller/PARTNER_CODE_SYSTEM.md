# Partner Code Generation System

## Overview

The Partner Code system in the Evolve Payments Platform generates unique, secure referral codes for resellers. Each reseller gets a unique code in the format `EVOLVE-XXXXXXXX` where X represents alphanumeric characters.

## Why Unique Partner Codes?

- **Security**: Prevents guessing of other resellers' codes
- **Professionalism**: Branded codes that represent the Evolve platform
- **Tracking**: Easy identification of referrals and commissions
- **Uniqueness**: No two resellers can have the same code

## How It Works

### 1. Code Generation Algorithm

The partner code generation uses a multi-factor approach to ensure uniqueness:

```python
# Located in: myapp/reseller/utils.py
def generate_partner_code(user_id=None, prefix="EVOLVE"):
    # Combines:
    # - User ID
    # - Current timestamp
    # - Random number (1000-9999)
    # - SHA-256 hashing
    # Result: EVOLVE-5A9GCAAJ (example)
```

**Process:**
1. Creates a unique string combining user ID, timestamp, and random number
2. Generates SHA-256 hash of this string
3. Takes first 8 characters of the hash
4. Converts to mixed alphanumeric format for readability
5. Prepends "EVOLVE-" prefix

### 2. Files Involved

#### Core Files:

1. **`myapp/reseller/utils.py`**
   - Contains `generate_partner_code()` function
   - Handles the actual code generation logic
   - Includes `format_partner_code()` for legacy code conversion

2. **`myapp/reseller/earnings/models/reseller.py`**
   - Defines `Reseller` model with `referral_code` field
   - Contains `generate_unique_referral_code()` class method
   - Ensures database-level uniqueness with retry logic

3. **`myapp/reseller/views.py`**
   - Creates reseller profiles with unique codes
   - Uses `Reseller.generate_unique_referral_code()` for new resellers
   - Handles code generation in dashboard, commissions, invoices, and payouts views

4. **`myapp/reseller/context_processors.py`**
   - Makes `partner_code` available globally in templates
   - Provides reseller context to all views

#### Template Files:

1. **`templates/dashboards/reseller/layouts/includes/reseller-header.html`**
   - Displays partner code in header: `{{ partner_code }}`

2. **`templates/dashboards/reseller/reseller-dashboard.html`**
   - Shows referral code in dashboard: `{{ referral_code }}`

#### Management Commands:

1. **`myapp/reseller/management/commands/update_partner_codes.py`**
   - Updates old format codes (REF-, RSL-, RESL-) to EVOLVE- format
   - Usage: `python manage.py update_partner_codes`

2. **`myapp/reseller/management/commands/regenerate_partner_codes.py`**
   - Regenerates all codes with new unique format
   - Usage: `python manage.py regenerate_partner_codes`
   - Supports dry-run mode: `--dry-run`
   - Can target specific user: `--user username`

#### Configuration:

1. **`EvolvePayments/config/settings.py`**
   - Registers context processor: `'myapp.reseller.context_processors.reseller_context'`
   - Makes partner code available in all templates

## Code Generation Example

When a new reseller is created:

```python
# User ID: 12
# Timestamp: 1721858220.123456
# Random: 5678

# Combined string: "12-1721858220.123456-5678"
# SHA-256 hash: "5a9fcaaj8b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
# First 8 chars: "5a9fcaaj"
# Final code: "EVOLVE-5A9FCAAJ"
```

## Database Structure

```sql
-- reseller_profiles table
referral_code VARCHAR(50) UNIQUE NOT NULL
-- Example: 'EVOLVE-5A9FCAAJ'
```

## Usage Flow

1. **New Reseller Registration**:
   - User signs up/logs in
   - System checks if reseller profile exists
   - If not, creates profile with unique code
   - Code is generated using `Reseller.generate_unique_referral_code()`

2. **Code Display**:
   - Context processor loads reseller's code
   - Available as `{{ partner_code }}` in all templates
   - Shown in header and dashboard

3. **Code Uniqueness**:
   - System attempts up to 10 times to generate unique code
   - Checks database for duplicates
   - If still not unique, appends timestamp

## Maintenance

### Updating Existing Codes

To update all existing codes to the new format:

```bash
# Update old format codes (REF-, RSL-, etc.) to EVOLVE-
python manage.py update_partner_codes

# Regenerate all codes with new unique algorithm
python manage.py regenerate_partner_codes

# Preview changes without applying them
python manage.py regenerate_partner_codes --dry-run

# Update specific user only
python manage.py regenerate_partner_codes --user john.doe
```

### Adding New Features

To modify the partner code system:

1. Update generation logic in `utils.py`
2. Test uniqueness with management commands
3. Update any views that create resellers
4. Run migrations if database changes needed

## Security Considerations

1. **Unpredictability**: Uses SHA-256 hashing with multiple random factors
2. **Uniqueness**: Database constraint prevents duplicates
3. **Non-sequential**: Cannot guess next code from previous ones
4. **Branded**: EVOLVE prefix prevents confusion with other systems

## Troubleshooting

### Common Issues:

1. **Duplicate Code Error**:
   - Run `regenerate_partner_codes` command
   - System will generate new unique code

2. **Missing Partner Code in Template**:
   - Ensure context processor is registered in settings
   - Check if user has reseller profile

3. **Old Format Codes (REF-, RSL-)**:
   - Run `update_partner_codes` command
   - Automatically converts to EVOLVE- format

## Future Enhancements

Potential improvements to consider:

1. Add QR code generation for partner codes
2. Include checksum digit for validation
3. Add expiration dates for codes
4. Implement code categories (Silver, Gold, Platinum)
5. Add analytics tracking for code usage

## Related Documentation

- [Reseller System Overview](README.md)
- [Commission Calculation](earnings/README.md)
- [Django Settings](../../EvolvePayments/config/settings.py)
