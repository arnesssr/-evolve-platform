# Reseller Earnings Module

This module contains all functionality related to reseller earnings management, including commissions, invoices, and payouts.

## Module Structure

```
earnings/
├── models/         # Data models for Commission, Invoice, Payout
├── services/       # Business logic for earnings operations
├── repositories/   # Data access layer for complex queries
├── forms/          # Django forms for user input
├── api/           # API endpoints for AJAX operations
└── __init__.py
```

## Components

### Models
- **Commission**: Tracks individual commission records from sales
- **Invoice**: Manages commission invoices and billing
- **Payout**: Handles payout requests and processing
- **Reseller**: Core reseller profile (shared across modules)

### Services
- **CommissionService**: Business logic for commission calculations and workflow
- **InvoiceService**: Invoice generation and management
- **PayoutService**: Payout request processing and validation

### Repositories
- **CommissionRepository**: Complex queries for commission data
- **InvoiceRepository**: Invoice-specific data access patterns
- **PayoutRepository**: Payout data retrieval and aggregation

### Forms
- **PayoutRequestForm**: Validates payout requests
- **InvoiceRequestForm**: Handles invoice generation requests

### API
- `/api/payouts/request/`: Process payout requests
- `/api/invoices/request/`: Generate invoices

## Usage

This module is imported by the main reseller views and admin:

```python
from myapp.reseller.earnings.models import Commission, Invoice, Payout
from myapp.reseller.earnings.services import CommissionService
```

## Related Templates

The earnings module serves these template pages:
- `/templates/dashboards/reseller/pages/earnings/commissions.html`
- `/templates/dashboards/reseller/pages/earnings/invoices.html`
- `/templates/dashboards/reseller/pages/earnings/payouts.html`

## Future Modules

The reseller app will be extended with additional modules:
- **sales/**: Lead management, referral tracking, sales reporting
- **marketing/**: Marketing tools, referral links, resources
- **analytics/**: Performance metrics and reporting
- **settings/**: Profile and configuration management
