# App Folder Structure
## Evolve Payments Platform - Main Django Application

This Django app follows a modular, scalable architecture with clear separation of concerns.

## Current Structure

```
App/
├── __init__.py               # App initialization
├── admin.py                  # Django built-in admin (for development)
├── models.py                 # Core application models
├── views.py                  # Core application views
├── urls.py                   # Main app URL routing
├── tests.py                  # Test cases
├── migrations/               # Database migrations
│
├── admin/                    # 🛡️ Admin Module (Platform Administration)
│   ├── models/              # Admin-specific models
│   ├── services/            # Admin business logic
│   ├── repositories/        # Admin data access
│   ├── api/v1/              # Admin REST API
│   ├── views/               # Admin dashboard views
│   ├── forms/               # Admin forms
│   └── README.md            # Admin module documentation
│
├── business/                 # 🏢 Business Module (Customer Dashboard)
│   ├── models/              # Business-specific models
│   ├── services/            # Business logic
│   ├── repositories/        # Business data access
│   ├── api/v1/              # Business REST API
│   ├── views/               # Business dashboard views
│   ├── forms/               # Business forms
│   └── README.md            # Business module documentation
│
├── reseller/                 # 🚀 Reseller Module (Partner Dashboard)
│   ├── earnings/            # Earnings management system
│   │   ├── models/         # Commission, Invoice, Payout models
│   │   ├── services/       # Earnings business logic
│   │   ├── repositories/   # Earnings data access
│   │   └── forms/          # Earnings forms
│   ├── api/v1/              # Reseller REST API
│   ├── views/               # Reseller dashboard views
│   └── README.md            # Reseller module documentation
│
└── integrations/             # 🔌 External Service Integrations
    ├── pesapal_service.py   # Pesapal payment gateway
    ├── utils.py             # Email/SMS communication
    └── __init__.py          # Integration module init
```

## Module Descriptions

### 🛡️ **Admin Module** (`App/admin/`)
**Purpose**: Platform administration system for Lixnet (platform owners)
- **User Management**: Manage businesses, resellers, and admin users
- **Financial Oversight**: Revenue analytics, commission tracking, billing management
- **System Monitoring**: Health checks, performance metrics, alert management
- **Configuration**: Platform settings, security controls, feature flags
- **Analytics**: Business intelligence, custom reports, data visualization

### 🏢 **Business Module** (`App/business/`)
**Purpose**: Customer dashboard for businesses who purchased Lixnet software
- **Product Access**: Quick launch to ERP, SACCO, Payroll systems
- **Subscription Management**: Plan details, billing center, usage tracking
- **Support System**: Ticket management, help center, knowledge base
- **Profile Management**: Company information, user management, settings
- **Analytics**: Usage metrics, performance insights, cost optimization

### 🚀 **Reseller Module** (`App/reseller/`)
**Purpose**: Partner dashboard for resellers who earn commissions
- **Earnings Management**: Commission tracking, invoice generation, payout requests
- **Sales Tools**: Lead management, referral tracking, pipeline management
- **Performance Analytics**: Conversion rates, tier progression, goal tracking
- **Marketing Resources**: Referral links, promotional materials, training
- **Profile System**: Partner verification, payment methods, tier management

### 🔌 **Integrations** (`App/integrations/`)
**Purpose**: External service integrations and communication utilities
- **Payment Processing**: Pesapal gateway integration
- **Communication**: Email/SMS services for notifications and OTP
- **Third-party APIs**: External service connections

### 📋 **Core App Files**
- **`admin.py`**: Django built-in admin interface (for development/emergency access)
- **`models.py`**: Core application models (OTP, UserProfile, Business, Plan, Feature)
- **`views.py`**: Main application views and authentication logic
- **`urls.py`**: URL routing and path configuration
- **`migrations/`**: Database schema changes and updates

## Architecture Principles

### **Clean Architecture**
- **Models**: Domain entities and data structure
- **Services**: Business logic and orchestration
- **Repositories**: Data access and persistence
- **Views**: Presentation and user interface
- **APIs**: External interface and integration

### **Separation of Concerns**
- Each module handles its specific domain
- External integrations are isolated
- Business logic is separated from presentation
- Data access is abstracted through repositories

### **Scalability**
- Modular structure allows independent development
- Each module can be scaled separately
- Easy to add new features without affecting other modules
- Can be split into microservices in the future

## Import Examples

```python
# Core models and views
from App.models import UserProfile, Business
from App.views import login_user, register_user

# External integrations
from App.integrations.utils import send_otp
from App.integrations.pesapal_service import generate_access_token

# Module-specific imports
from App.reseller.earnings.services.commission_service import CommissionService
from App.admin.services.analytics_service import PlatformAnalyticsService
from App.business.services.subscription_service import SubscriptionService
```

## Benefits

1. **🏗️ Modular Architecture**: Clear separation of different user types and their functionality
2. **🔧 Maintainable**: Easy to locate and modify specific features
3. **📈 Scalable**: Each module can grow independently
4. **🧪 Testable**: Isolated modules with clear dependencies
5. **👥 Team-Friendly**: Multiple developers can work on different modules
6. **🚀 Future-Proof**: Easy to extract modules into separate services
7. **📝 Self-Documenting**: Clear module purposes and responsibilities
