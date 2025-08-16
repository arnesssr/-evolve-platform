# Reseller Models Documentation

## Overview
This directory contains the core data models for the reseller module of the Evolve Payments Platform. These models handle the entire lifecycle of reseller partnerships, from profile management to commission tracking and payout processing.

## Architecture Philosophy
The models are designed following Django best practices with:
- **Separation of Concerns**: Each model handles a specific domain
- **Data Integrity**: Proper relationships and constraints
- **Performance**: Strategic indexing and query optimization
- **Extensibility**: Easy to add new features without breaking existing functionality

## Models Structure

### 1. Base Models (`base.py`)
**Purpose**: Provides abstract base classes and choice fields used across the module.

**Key Components**:
- `TimeStampedModel`: Abstract model that adds `created_at` and `modified_at` timestamps to all models
- Status choices for different model states (Commission, Invoice, Payout)
- Payment method choices
- Tier choices for reseller levels

**Why Created**: To maintain consistency across all models and avoid code duplication.

### 2. Reseller Model (`reseller.py`)
**Purpose**: Core profile model for resellers/partners.

**Key Features**:
- Links to Django User model (one-to-one relationship)
- Stores company information and contact details
- Manages tier system (Bronze, Silver, Gold, Platinum)
- Tracks financial metrics (total sales, commissions earned/paid)
- Handles payment information for different payout methods

**Key Methods**:
- `get_available_balance()`: Calculates withdrawable balance
- `get_tier_commission_rate()`: Returns commission rate based on tier
- `update_tier()`: Automatically updates tier based on performance

**Why Created**: Central model to manage all reseller-related data and business logic.

### 3. Commission Model (`commission.py`)
**Purpose**: Tracks individual commission records for each sale/transaction.

**Key Features**:
- Links to reseller profile
- Stores transaction details (reference, client info, product)
- Tracks commission lifecycle (pending → approved → paid)
- Supports tier bonuses
- Links to invoices and payouts for complete audit trail

**Key Fields**:
- `transaction_reference`: Unique identifier for the sale
- `sale_amount`: Original transaction amount
- `amount`: Calculated commission amount
- `commission_rate`: Rate applied for this commission
- `status`: Current state in approval workflow

**Why Created**: To provide granular tracking of each commission earned, enabling detailed reporting and proper financial management.

### 4. Invoice Model (`invoice.py`)
**Purpose**: Manages commission invoices for resellers.

**Key Features**:
- Auto-generates unique invoice numbers
- Groups commissions by period
- Tracks invoice lifecycle (draft → sent → paid)
- Supports PDF generation and storage
- Handles overdue detection

**Key Methods**:
- `generate_invoice_number()`: Creates sequential invoice numbers
- `calculate_total()`: Sums up related commissions
- `mark_as_paid()`: Updates status and payment date
- `is_overdue`: Property to check if payment is late

**Why Created**: To provide professional invoicing capability and maintain proper financial records for tax and accounting purposes.

### 5. Payout Model (`payout.py`)
**Purpose**: Handles withdrawal requests and payout processing.

**Key Features**:
- Tracks payout requests from resellers
- Supports multiple payment methods
- Manages approval workflow
- Calculates net amounts after fees
- Updates reseller balances upon completion

**Key Methods**:
- `process_payout()`: Moves payout to processing state
- `complete_payout()`: Finalizes payout and updates balances
- `fail_payout()`: Handles failed transactions

**Why Created**: To manage the actual money transfer process with proper approval workflows and audit trails.

## Model Relationships

```
User (Django Auth)
    ↓ (One-to-One)
Reseller
    ↓ (One-to-Many)
Commission ←→ Invoice (Many-to-Many)
    ↓ (Many-to-One)
Payout
```

## Usage Examples

### Creating a Reseller Profile
```python
from myapp.reseller.models import Reseller
from django.contrib.auth.models import User

user = User.objects.get(username='john_doe')
reseller = Reseller.objects.create(
    user=user,
    company_name='ABC Marketing',
    referral_code='ABC123',
    tier='bronze',
    commission_rate=10.00
)
```

### Recording a Commission
```python
from myapp.reseller.models import Commission

commission = Commission.objects.create(
    reseller=reseller,
    transaction_reference='TXN-2024-001',
    client_name='XYZ Corp',
    product_name='Premium Plan',
    sale_amount=1000.00,
    commission_rate=10.00,
    amount=100.00  # 10% of 1000
)
```

### Creating an Invoice
```python
from myapp.reseller.models import Invoice
from datetime import date

invoice = Invoice.objects.create(
    reseller=reseller,
    period_start=date(2024, 1, 1),
    period_end=date(2024, 1, 31),
    due_date=date(2024, 2, 15)
)

# Link commissions to invoice
commission.invoice = invoice
commission.save()

# Calculate total
invoice.calculate_total()
```

### Processing a Payout
```python
from myapp.reseller.models import Payout

payout = Payout.objects.create(
    reseller=reseller,
    amount=500.00,
    payment_method='bank_transfer'
)

# Process the payout
payout.process_payout()

# Complete after payment is made
payout.complete_payout(transaction_reference='BANK-REF-123')
```

## Database Considerations

### Indexes
- `Reseller.referral_code` - For quick lookups
- `Commission.transaction_reference` - Unique constraint
- `Invoice.invoice_number` - Unique constraint
- `Payout.reference_number` - Unique constraint

### Performance Tips
1. Use `select_related()` when fetching commissions with reseller data
2. Use `prefetch_related()` when fetching invoices with multiple commissions
3. Regular archival of old paid commissions recommended

## Admin Interface
All models are registered in `admin.py` with:
- Custom list displays
- Filters for easy searching
- Bulk actions for status updates
- Readonly fields for calculated values
- Formatted status badges

## Future Enhancements
1. **Audit Trail**: Add detailed logging of all changes
2. **Multi-currency**: Support for different currencies
3. **Automated Calculations**: Signals to auto-calculate commissions
4. **Notifications**: Email/SMS alerts for status changes
5. **API Integration**: RESTful endpoints for external systems

## Testing
When testing these models:
1. Always test the full lifecycle (create → approve → pay)
2. Test edge cases (negative amounts, invalid status transitions)
3. Verify calculations are accurate
4. Test concurrent updates to avoid race conditions

## Maintenance
1. Run migrations after any model changes
2. Update admin configurations when adding fields
3. Document any custom business logic
4. Keep status choices synchronized with frontend
