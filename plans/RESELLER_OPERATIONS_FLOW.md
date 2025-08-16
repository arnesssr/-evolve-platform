# Reseller Operations Flow Diagram

## How Resellers Interact with the Evolve Payments Platform

```
                              RESELLER LIFECYCLE FLOW
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  1. RESELLER ONBOARDING                                           │
    │  ┌─────────────┐                                                  │
    │  │   Reseller  │ ──── Signs up ────► Partnership Tier Assignment │
    │  │  (Partner)  │                      (Basic/Silver/Gold/Platinum)│
    │  └─────────────┘                                                  │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  2. LEAD GENERATION & REFERRALS                                    │
    │                                                                     │
    │   Reseller finds clients ──────► Registers leads in system        │
    │          │                                    │                    │
    │          ▼                                    ▼                    │
    │   • Small businesses              • Tracks referral source        │
    │   • Merchants                     • Lead status (Hot/Warm/Cold)   │
    │   • Retail shops                  • Contact information            │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  3. SALES CONVERSION                                               │
    │                                                                     │
    │   Lead ──► Demo ──► Negotiation ──► Client signs up for:          │
    │                                      • Payment processing          │
    │                                      • POS systems                 │
    │                                      • Other Evolve services       │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  4. COMMISSION EARNING                                             │
    │                                                                     │
    │   Client makes transactions ────► System calculates commission     │
    │            │                           │                           │
    │            ▼                           ▼                           │
    │   $1,000 transaction          • Base rate: 2-5%                  │
    │   $5,000 transaction          • Tier bonus: 0.5-2%               │
    │   $10,000 transaction         • Volume bonus                      │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  5. EARNINGS MANAGEMENT                                            │
    │                                                                     │
    │  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐      │
    │  │ Commissions  │────►│   Invoices   │────►│   Payouts    │      │
    │  │              │     │              │     │              │      │
    │  │ • Pending    │     │ • Generated  │     │ • Requested  │      │
    │  │ • Approved   │     │ • Sent       │     │ • Processing │      │
    │  │ • Paid       │     │ • Paid       │     │ • Completed  │      │
    │  └──────────────┘     └──────────────┘     └──────────────┘      │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  6. RESELLER DASHBOARD ACCESS                                      │
    │                                                                     │
    │  📊 View:                         💰 Manage:                       │
    │  • Total earnings                 • Request payouts                │
    │  • Active clients                 • Download invoices              │
    │  • Commission history             • Update payment methods         │
    │  • Performance metrics            • View transaction details       │
    │  • Lead pipeline                  • Track referral status          │
    └─────────────────────────────────────────────────────────────────────┘

    
    REAL-WORLD EXAMPLE:
    ═══════════════════════════════════════════════════════════════════════
    
    John (Reseller) ──► Refers ABC Store ──► ABC Store processes $50,000/month
           │                    │                         │
           │                    │                         ▼
           │                    │                  John earns 3% = $1,500
           │                    │                         │
           │                    ▼                         ▼
           │              Referral tracked          Commission approved
           │                    │                         │
           ▼                    ▼                         ▼
    Views dashboard      Gets notification        Requests monthly payout
                                                         │
                                                         ▼
                                                  Receives payment
```

## Key Process Steps Explained

### 1. Reseller Onboarding
- New resellers register on the platform
- System assigns partnership tier based on criteria
- Tiers determine commission rates and benefits

### 2. Lead Generation & Referrals
- Resellers identify potential clients in their network
- Register leads with contact details and status
- System tracks the source and progress of each referral

### 3. Sales Conversion
- Resellers guide leads through the sales process
- Includes product demos and negotiations
- Successful conversions become active clients

### 4. Commission Earning
- System automatically tracks client transactions
- Calculates commissions based on:
  - Base commission rate (tier-dependent)
  - Tier bonuses for higher partnership levels
  - Volume bonuses for high-performing resellers

### 5. Earnings Management
- **Commissions**: Track pending, approved, and paid commissions
- **Invoices**: Generate and manage payment invoices
- **Payouts**: Request and track payment disbursements

### 6. Dashboard Access
- Central hub for all reseller activities
- Real-time visibility into performance and earnings
- Self-service management of payouts and account settings

## Benefits for Resellers

1. **Passive Income**: Earn ongoing commissions from referred clients
2. **Transparent Tracking**: Clear visibility of all referrals and earnings
3. **Automated Processing**: System handles commission calculations
4. **Flexible Payouts**: Request payments when needed
5. **Growth Incentives**: Higher tiers unlock better rates

## Technical Implementation Notes

- This flow integrates with the backend architecture defined in RESELLER_BACKEND_ARCHITECTURE.md
- Dashboard UI implementation detailed in RESELLER_DASHBOARD_UI_PLAN.md
- API endpoints support all operations in this flow
