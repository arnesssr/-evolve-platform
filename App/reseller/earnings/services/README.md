# Reseller Services

This directory contains the service classes that encapsulate business logic for the reseller module, focusing on commission, invoice, and payout management.

## Service Components

### 1. BaseService (`base.py`)
Provides common functionalities for all services, including logging, transaction management, and validation utilities.

**Key Features:**
- Logging support for actions and errors
- Atomic transaction execution
- Common validation logic

**Usage:**
```python
base_service = BaseService()
base_service.log_info('Operation successful')
```

### 2. CommissionService (`commission_service.py`)
Handles all operations related to resellers' commissions, such as creation, approval, and payment.

**Key Features:**
- Commission creation based on sales transactions
- Workflow management (pending, approved, paid commissions)
- Summary and reporting tools

**Usage:**
```python
commission_service = CommissionService()
commission_service.create_commission(transaction_data)
```

### 3. InvoiceService (`invoice_service.py`)
Manages the generation and lifecycle of commission invoices.

**Key Features:**
- Automated invoice generation from commissions
- Invoice sending and payment tracking
- Management of invoice states (draft, sent, paid)

**Usage:**
```python
invoice_service = InvoiceService()
invoice_service.generate_invoice_from_commissions(reseller, period_start, period_end)
```

### 4. PayoutService (`payout_service.py`)
Oversees payout requests and processing for resellers.

**Key Features:**
- Request and process payouts
- Validation against available balances
- Management of payout lifecycle and methods

**Usage:**
```python
payout_service = PayoutService()
payout_service.request_payout(reseller, amount, payment_method)
```

### 5. ResellerService (`reseller_service.py`) 🆕
Manages reseller profile operations and business logic.

**Key Features:**
- Profile creation and updates
- Profile verification workflow
- Profile completion tracking
- Tier management and updates
- Comprehensive statistics generation
- Profile activation/deactivation

**Usage:**
```python
reseller_service = ResellerService()
# Create profile
reseller = reseller_service.create_reseller_profile(user, profile_data)
# Update profile
updated_reseller = reseller_service.update_profile(reseller_id, profile_data)
# Get profile completion status
completion_status = reseller_service.get_profile_completion_status(reseller_id)
# Get comprehensive stats
stats = reseller_service.get_reseller_stats(reseller_id)
```

## Integration

Services are utilized by:
- **Views**: To execute business logic in response to user actions
- **API**: To handle operations exposed via endpoints
- **Repositories**: When advanced queries or data access patterns are needed

## Benefits

1. **Separation of Concerns**: Distills business logic from data access and presentation layers
2. **Reusability**: Centralizes logic that can be reused across different components
3. **Maintainability**: Simplifies modification of business rules without altering views or models

## Future Enhancements
1. **Caching**: Add caching to improve performance of repeated data retrieval
2. **Audit Logging**: Record key operations for compliance and review
3. **Error Handling**: Enhance error reporting for better debugging
