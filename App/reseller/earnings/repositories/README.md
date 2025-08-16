# Reseller Repositories

This directory contains repository classes that encapsulate database access logic for the reseller module. The repository pattern is used to abstract and centralize complex queries, making data access more organized and maintainable.

## Repository Components

### 1. BaseRepository (`base.py`)
Provides common data access methods shared by all repositories.

**Key Features:**
- CRUD operations (create, read, update, delete)
- Filtering and exclusion methods
- Bulk operations
- Pagination support

### 2. CommissionRepository (`commission_repository.py`)
Handles queries specific to the `Commission` model.

**Core Methods:**
- `get_pending_commissions()` - Retrieves pending commissions for optional reseller
- `get_commissions_for_period()` - Fetches commissions based on date range
- `calculate_total_pending()` - Calculates total outstanding pending commissions
- `search_commissions()` - Full-text search across commission fields

### 3. InvoiceRepository (`invoice_repository.py`)
Manages database operations for the `Invoice` model.

**Core Methods:**
- `get_overdue_invoices()` - Finds invoices past their due date
- `calculate_yearly_total()` - Computes total invoiced amounts per year
- `get_next_invoice_number()` - Generates the next unique invoice identifier
- `search_invoices()` - Search invoices by description and number

### 4. PayoutRepository (`payout_repository.py`)
Facilitates access to `Payout` related data.

**Core Methods:**
- `get_pending_payouts()` - Retrieves payouts awaiting completion
- `calculate_total_paid()` - Computes the total amount disbursed
- `get_monthly_payout_stats()` - Generates monthly payout statistics for the past year
- `search_payouts()` - Search payouts via reference numbers

### 5. ResellerRepository (`reseller_repository.py`) 🆕
Manages database operations for the `Reseller` model.

**Core Methods:**
- `get_by_user_id()` - Retrieves reseller by user ID
- `get_by_referral_code()` - Finds reseller by their unique referral code
- `get_active_resellers()` - Returns all active resellers
- `get_verified_resellers()` - Returns verified resellers only
- `verify_reseller()` - Updates reseller verification status
- `search()` - Advanced search with multiple filters (tier, status, commission range)
- `get_top_performers()` - Returns top resellers by sales volume
- `get_recent_signups()` - Finds recently joined resellers
- `update_metrics()` - Updates reseller performance metrics
- `get_incomplete_profiles()` - Identifies profiles missing required information

## Benefits of Using Repositories

1. **Separation of Concerns:**
   - Keeps data access separate from business logic present in services
   - Promotes readable and testable code by isolating query logic

2. **Reusability:**
   - Centralize complex queries to avoid repetition
   - Repositories can be reused across services and views

3. **Maintainability:**
   - Simplifies updates to the data access pattern
   - Encapsulates frequently changing query logic

## Usage Patterns

### In Services
```python
from myapp.reseller.repositories import CommissionRepository

repo = CommissionRepository()
commissions = repo.get_pending_commissions(reseller=my_reseller)
```

### In Views
```python
from myapp.reseller.repositories import InvoiceRepository

repo = InvoiceRepository()
overdue_invoices = repo.get_overdue_invoices()
```

## Future Enhancements
1. **Advanced Caching:** Implement query caching for frequently accessed data.
2. **Soft Deletes:** Add support for soft deleting records.
3. **Complex Joins:** Support for aggregations involving joins across models.
4. **Dynamic Filtering:** Create a flexible API for building dynamic queries.
5. **Batch Processing:** Optimize batch retrievals and processing in high-volume scenarios.
