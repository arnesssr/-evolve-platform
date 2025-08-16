# Evolve Payments Platform

A B2B software marketplace and referral platform that connects software vendors with resellers, enabling commission-based sales of business software solutions across African markets.

## 🎯 What is this platform?

This is a referral/reseller system where:
- **Lixnet (Platform Owner)** owns and sells their software products (ERP, SACCO, Payroll systems)
- **Resellers** register to promote Lixnet's products to potential business customers
- **Businesses** are the end customers who purchase and use Lixnet's software products
- **Resellers earn commissions** when they successfully refer customers who purchase

## 👥 User Roles

1. **Admin (Platform Owner)**
   - Manages the entire platform
   - Approves vendor listings
   - Monitors transactions and commissions
   - Has full visibility of all resellers and businesses

2. **Business (Customer)**
   - End customers who purchase Lixnet's software products
   - Uses the platform to access their purchased software (ERP, SACCO, Payroll)
   - Manages their subscription and account
   - Tracks their usage and invoices

3. **Reseller**
   - Registers to become a sales agent
   - Promotes vendor products to potential customers
   - Earns commission on successful referrals
   - Tracks their sales performance

## 🚀 Features

- **Multi-tenant System**: Support for Vendors, Resellers, and Admin roles
- **Secure Authentication**: Two-factor authentication with OTP via SMS and Email
- **Payment Integration**: Pesapal payment gateway for subscription and commission payments
- **Commission Tracking**: Automated commission calculation and tracking
- **Product Marketplace**: Vendors can list multiple software products
- **Referral Management**: Track referrals from initial contact to successful sale
- **African Market Focus**: Optimized for 54 African countries

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- PowerShell (for Windows users)

## 🛠️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/JoyNyayieka/evolve-payments-platform.git
cd evolve-payments-platform
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv evolve_env
.\evolve_env\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv evolve_env
source evolve_env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory with the following variables:
```env
# SMS Configuration
SMSLEOPARD_API_KEY=your_api_key
SMSLEOPARD_API_SECRET=your_api_secret

# Pesapal Configuration (add when you have credentials)
PESAPAL_CONSUMER_KEY=your_consumer_key
PESAPAL_CONSUMER_SECRET=your_consumer_secret
PESAPAL_BASE_URL=https://pay.pesapal.com/v3
```

### 5. Apply database migrations
```bash
python manage.py migrate
```

### 6. Run the development server

**Option 1 - Using PowerShell script (Windows):**
```powershell
.\run_server.ps1
```

**Option 2 - Manual command:**
```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## 🔧 Development

### Adding new dependencies
When you add a new Python package:
1. Install it: `pip install package_name`
2. Add it to requirements.txt: `package_name==version`
3. Get the version: `pip show package_name`
4. Commit both files together

### Creating a superuser (admin)
```bash
python manage.py createsuperuser
```

### Running tests
```bash
python manage.py test
```

## 📁 Project Structure
```
evolve-payments-platform/
├── EvolvePayments/     # Main Django project settings
├── myapp/              # Main application
│   ├── models.py       # Database models
│   ├── views.py        # View controllers
│   ├── urls.py         # URL routing
│   └── templates/      # HTML templates
├── static/             # Static files (CSS, JS, images)
├── templates/          # Global templates
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── run_server.ps1      # PowerShell script to run server
└── .env                # Environment variables (not in git)
```

## 🤝 Contributing
Please ensure to update tests as appropriate and update the requirements.txt file when adding new dependencies.

## 📝 License
This project is proprietary software. All rights reserved.
# Team Collaboration Update
