# Reseller Backend Architecture Plan
## Clean, Scalable Django Structure with Separation of Concerns

### 🎯 Core Principles
1. **Separation of Concerns**: Clear boundaries between layers
2. **DRY (Don't Repeat Yourself)**: Reusable components
3. **SOLID Principles**: Maintainable and extensible code
4. **Fat Models, Thin Views**: Business logic in models/services
5. **Repository Pattern**: Abstract data access

---

## 📁 Directory Structure

```
evolve-payments-platform/
├── App/                            # Main Django app
│   ├── reseller/                   # Reseller module ✅ DONE
│   ├── admin/                      # Admin module ✅ CREATED
│   └── business/                   # Business module ✅ CREATED
│       ├── __init__.py
│       ├── apps.py                 # App configuration
│       │
│       ├── models/                 # Domain models (Entity Layer)
│       │   ├── __init__.py        ✅ DONE
│       │   ├── base.py            ✅ DONE - Base model classes
│       │   ├── reseller.py        ✅ DONE - Reseller profile model (includes tier system)
│       │   ├── lead.py            ❌ TODO - Lead/prospect models
│       │   ├── referral.py        ❌ TODO - Referral tracking
│       │   ├── commission.py      ✅ DONE - Commission calculation
│       │   ├── invoice.py         ✅ DONE - Invoice management
│       │   ├── payout.py          ✅ DONE - Payout processing
│       │   ├── tier.py            ✅ INTEGRATED - Tier system integrated in reseller.py
│       │   └── activity.py        ❌ TODO - Activity logging
│       │
│       ├── services/               # Business Logic Layer
│       │   ├── __init__.py        ✅ DONE
│       │   ├── base.py            ✅ DONE - Base service class
│       │   ├── reseller_service.py     ✅ DONE - Reseller operations
│       │   ├── lead_service.py         ❌ TODO - Lead management logic
│       │   ├── referral_service.py     ❌ TODO - Referral processing
│       │   ├── commission_service.py   ✅ DONE - Commission calculations
│       │   ├── invoice_service.py      ✅ DONE - Invoice management
│       │   ├── payout_service.py       ✅ DONE - Payout processing
│       │   ├── notification_service.py ❌ TODO - Notification handling
│       │   └── analytics_service.py    ❌ TODO - Analytics & reporting
│       │
│       ├── repositories/           # Data Access Layer
│       │   ├── __init__.py        ✅ DONE
│       │   ├── base.py            ✅ DONE - Base repository class
│       │   ├── reseller_repository.py  ✅ DONE - Reseller data access
│       │   ├── lead_repository.py      ❌ TODO
│       │   ├── referral_repository.py  ❌ TODO
│       │   ├── commission_repository.py ✅ DONE
│       │   ├── invoice_repository.py    ✅ DONE
│       │   └── payout_repository.py     ✅ DONE
│       │
│       ├── api/                    # API Layer (REST)
│       │   ├── __init__.py        ✅ DONE
│       │   ├── views.py           ✅ DONE - Payout & Invoice endpoints
│       │   ├── urls.py            ✅ DONE - API routing
│       │   ├── v1/                ✅ PARTIAL - API version 1
│       │   │   ├── __init__.py    ✅ DONE
│       │   │   ├── serializers/   # DRF Serializers
│       │   │   │   ├── __init__.py ✅ DONE
│       │   │   │   ├── reseller_serializers.py ✅ DONE - 7 serializers
│       │   │   │   ├── lead_serializers.py ❌ TODO
│       │   │   │   ├── referral_serializers.py ❌ TODO
│       │   │   │   └── commission_serializers.py ❌ TODO
│       │   │   ├── views/         # API Views
│       │   │   │   ├── __init__.py ✅ DONE
│       │   │   │   ├── reseller_views.py ✅ DONE - ResellerViewSet
│       │   │   │   ├── lead_views.py ❌ TODO
│       │   │   │   ├── referral_views.py ❌ TODO
│       │   │   │   └── commission_views.py ❌ TODO
│       │   │   ├── filters/       # Query filters
│       │   │   │   ├── __init__.py ❌ TODO
│       │   │   │   └── reseller_filters.py ❌ TODO
│       │   │   └── urls.py        # API URL patterns ❌ TODO
│       │   └── permissions.py     ❌ TODO - Custom permissions
│       │
│       ├── views.py               ✅ DONE - Base view functions
│       ├── views/                  ✅ PARTIAL - Traditional Django Views
│       │   ├── __init__.py        ✅ DONE
│       │   ├── profile_views.py   ✅ DONE - 8 profile management views
│       │   ├── dashboard_views.py ❌ TODO - Dashboard pages
│       │   ├── lead_views.py      ❌ TODO - Lead management pages
│       │   ├── referral_views.py  ❌ TODO - Referral pages
│       │   └── report_views.py    ❌ TODO - Reporting pages
│       │
│       ├── forms/                  # Django Forms
│       │   ├── __init__.py        ✅ DONE
│       │   ├── payout_forms.py    ✅ DONE - Payout request form
│       │   ├── invoice_forms.py   ✅ DONE - Invoice request form
│       │   ├── profile_forms.py   ✅ DONE - 4 profile forms
│       │   ├── lead_forms.py      ❌ TODO
│       │   └── referral_forms.py  ❌ TODO
│       │
│       ├── managers/               # Custom Model Managers
│       │   ├── __init__.py
│       │   ├── reseller_manager.py
│       │   ├── lead_manager.py
│       │   └── commission_manager.py
│       │
│       ├── utils/                  # Utility functions
│       │   ├── __init__.py
│       │   ├── calculations.py    # Commission calculations
│       │   ├── validators.py      # Custom validators
│       │   ├── helpers.py         # Helper functions
│       │   └── constants.py       # App constants
│       │
│       ├── exceptions/             # Custom exceptions
│       │   ├── __init__.py
│       │   └── reseller_exceptions.py
│       │
│       ├── signals/                # Django signals
│       │   ├── __init__.py
│       │   ├── handlers.py        # Signal handlers
│       │   └── signals.py         # Custom signals
│       │
│       ├── tasks/                  # Async tasks (Celery)
│       │   ├── __init__.py
│       │   ├── email_tasks.py
│       │   ├── notification_tasks.py
│       │   └── analytics_tasks.py
│       │
│       ├── tests/                  # Test suite
│       │   ├── __init__.py
│       │   ├── test_models/
│       │   ├── test_services/
│       │   ├── test_api/
│       │   ├── test_views/
│       │   └── factories.py       # Test factories
│       │
│       ├── migrations/             ✅ DONE - Initial migration created
│       ├── admin.py               ✅ DONE - Django admin
│       ├── urls.py                ✅ DONE - URL patterns with profile routes
│       ├── permissions.py         ✅ DONE - Access control
│       └── middleware.py          ❌ TODO - Custom middleware
│
├── core/                          # Core/Shared functionality
│   ├── __init__.py
│   ├── models/                    # Base/Abstract models
│   │   ├── __init__.py
│   │   ├── base.py               # TimeStampedModel, etc.
│   │   └── mixins.py             # Model mixins
│   ├── services/                  # Shared services
│   │   ├── __init__.py
│   │   ├── email_service.py
│   │   ├── sms_service.py
│   │   └── payment_service.py
│   ├── utils/                     # Shared utilities
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── pagination.py
│   │   └── responses.py
│   └── exceptions.py              # Base exceptions
│
├── config/                        # Project configuration
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py               # Base settings
│   │   ├── development.py        # Dev settings
│   │   ├── production.py         # Prod settings
│   │   └── testing.py            # Test settings
│   ├── urls.py                   # Root URL config
│   └── wsgi.py
│
├── templates/                     # Templates
│   └── dashboards/
│       └── reseller/             # Reseller templates
│           └── pages/
│               ├── earnings/     # Earnings pages
│               │   ├── commissions.html
│               │   ├── invoices.html
│               │   └── payouts.html
│               ├── sales/        # Sales pages
│               └── marketing/    # Marketing pages
│
└── requirements/                  # Dependencies
    ├── base.txt                  # Base requirements
    ├── development.txt           # Dev requirements
    └── production.txt            # Prod requirements
```

---

## 🏗️ Layer Architecture

### 1. **Models Layer** (Domain Layer)

### 2. **Repository Layer** (Data Access)

### 3. **Service Layer** (Business Logic)

### 4. **API Layer** (REST Interface)

### 5. **View Layer** (Django Views)

---

## 🚀 Implementation Roadmap

### Phase 1: Core Earnings Features (Priority) ✅ COMPLETED
Focus on the money flow - what resellers care about most.

#### 1. **Commission System** ✅ DONE
- ✅ Commission model with calculation tracking
- ✅ Commission approval workflow
- ✅ Commission history and reporting
- ✅ Integration with existing transactions

#### 2. **Invoice Management** ✅ DONE
- ✅ Invoice generation from commissions
- ✅ Invoice status tracking
- ❌ PDF generation for invoices (TODO)
- ✅ Invoice history view

#### 3. **Payout Processing** ✅ DONE
- ✅ Payout request system
- ✅ Payout approval workflow
- ✅ Payment method management
- ✅ Payout history and tracking

### 🔄 WORK IN PROGRESS (Current Sprint)

#### 1. **Reseller Profile Management** ✅ COMPLETED
- [x] Reseller model enhancement (contact info, business details)
- [x] Profile service layer (ResellerService)
- [x] Profile repository (ResellerRepository)
- [x] Profile forms and views (4 forms, 8 views)
- [x] Profile API endpoints (ResellerViewSet with custom actions)

#### 2. **Lead & Referral System** 🚧 IN PROGRESS
- [ ] Lead model (lead.py)
- [ ] Referral model (referral.py)
- [ ] Lead service (lead_service.py)
- [ ] Referral service (referral_service.py)
- [ ] Lead and referral repositories
- [ ] Lead management views and forms

#### 3. **Tier System** ✅ MOSTLY COMPLETE (Integrated in Reseller Model)
- [x] Tier model (integrated in reseller.py instead of separate model)
- [x] Tier assignment logic (update_tier method)
- [x] Commission rate calculation based on tiers (get_tier_commission_rate)
- [x] Tier progression rules (Bronze→Silver→Gold→Platinum based on sales)

#### 4. **Dashboard Views** 🚧 IN PROGRESS
- [ ] Main dashboard view (dashboard_views.py)
- [ ] Earnings overview widget
- [ ] Lead pipeline widget
- [ ] Performance metrics widget
- [ ] Recent activity feed

#### 5. **API v1 Structure** 🚧 IN PROGRESS
- [x] Create api/v1/ directory structure
- [x] Base serializers (7 reseller serializers completed)
- [x] Base viewsets (ResellerViewSet completed)
- [ ] Pagination implementation
- [ ] Custom API permissions
- [ ] API documentation (Swagger/OpenAPI)

### Phase 2: Sales & Lead Management
- Lead tracking and conversion
- Referral system
- Sales reporting

### Phase 3: Advanced Features
- Tier system implementation
- Analytics dashboard
- API endpoints for external integration

---

## 💰 Earnings Module Design Details

### Commission Model Structure
```python
class Commission(models.Model):
    reseller = models.ForeignKey('Reseller', on_delete=models.CASCADE)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    tier_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20)  # pending, approved, paid
    calculation_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
```

### Invoice Model Structure
```python
class Invoice(models.Model):
    reseller = models.ForeignKey('Reseller', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    commissions = models.ManyToManyField('Commission')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # draft, sent, paid
    issue_date = models.DateField()
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
```

### Payout Model Structure
```python
class Payout(models.Model):
    reseller = models.ForeignKey('Reseller', on_delete=models.CASCADE)
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # requested, processing, completed, failed
    payment_method = models.CharField(max_length=50)  # bank_transfer, paypal, etc
    request_date = models.DateTimeField(auto_now_add=True)
    process_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    failure_reason = models.TextField(blank=True)
```

---

## 🔧 Key Design Patterns

### 1. **Repository Pattern**
- Abstracts data access logic
- Makes testing easier (mock repositories)
- Allows switching data sources

### 2. **Service Layer Pattern**
- Contains business logic
- Coordinates between repositories
- Handles transactions and complex operations

### 3. **Factory Pattern** (for tests)

### 4. **Manager Pattern**

---

## 📋 Implementation Guidelines

### 1. **Model Guidelines**
- Keep models focused on data structure
- Use custom managers for complex queries
- Implement model methods for simple business logic
- Use signals sparingly

### 2. **Service Guidelines**
- One service per domain area
- Services orchestrate operations
- Handle transactions at service level
- Services can call other services

### 3. **Repository Guidelines**
- One repository per model
- Only data access logic
- Return model instances or querysets
- No business logic

### 4. **API Guidelines**
- Version your APIs (/api/v1/)
- Use serializers for validation
- Implement proper pagination
- Use ViewSets for CRUD operations

### 5. **Testing Strategy**

---

## 🚀 Benefits of This Structure

1. **Scalability**
   - Easy to add new features
   - Clear boundaries between layers
   - Can split into microservices later

2. **Testability**
   - Each layer can be tested independently
   - Easy to mock dependencies
   - Clear test organization

3. **Maintainability**
   - Clear separation of concerns
   - Easy to understand code flow
   - Consistent patterns

4. **Team Collaboration**
   - Clear ownership boundaries
   - Parallel development possible
   - Less merge conflicts

5. **Performance**
   - Optimized queries in repositories
   - Caching at service layer
   - Efficient data access patterns

This structure provides a solid foundation for building a robust, scalable reseller backend system using Django.
