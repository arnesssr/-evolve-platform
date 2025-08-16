# Reseller Dashboard Redesign Plan
## Evolve Payments Platform - Reseller Dashboard

### 🎯 Understanding the Reseller Dashboard
- **Resellers are sales partners** who promote and sell Lixnet's software products
- They earn commissions on successful referrals and sales
- The dashboard helps them track performance, earnings, and manage referrals

---

## 📐 UI/UX Design Mockups

### 1. Modern Reseller Dashboard Layout
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TOP NAVIGATION BAR                                                          │
│ ┌─────────────┬──────────────────────────────────┬────────────────────┐   │
│ │ ☰ 🚀 Evolve │  Welcome back, {{Reseller Name}} │ 🔔 👤 Help ⚙️      │   │
│ │   Reseller  │  Partner Code: RESL-2098         │                    │   │
│ └─────────────┴──────────────────────────────────┴────────────────────┘   │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │ BREADCRUMB & PAGE HEADER                                     │
│   SIDEBAR    │ ┌────────────────────────────────────────────────────────┐  │
│              │ │ Dashboard > Overview                                    │  │
│ ┌──────────┐ │ ├────────────────────────────────────────────────────────┤  │
│ │ 📊 Home  │ │ │ Reseller Dashboard                     [This Month ▼]│  │
│ │ ───────  │ │ └────────────────────────────────────────────────────────┘  │
│ │          │ │                                                              │
│ │ SALES    │ │ PERFORMANCE METRICS                                         │
│ │ 🎯 Leads │ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│ │ 🤝 Referr│ │ │ Total Sales │ │ Commission  │ │ Conversion  │ │ Tier   │ │
│ │ 📈 Report│ │ │ 23          │ │ KES 45,000  │ │ Rate: 18%   │ │ Silver │ │
│ │          │ │ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
│ │ EARNINGS │ │                                                              │
│ │ 💰 Commis│ │ REFERRAL PIPELINE                                           │
│ │ 📋 Invoice│ │ ┌────────────────────────────────────────────────────────┐  │
│ │ 💳 Payout│ │ │ Active Referrals                        [+ New Lead] 🔍 │  │
│ │          │ │ ├────────────────────────────────────────────────────────┤  │
│ │ TOOLS    │ │ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │  │
│ │ 🔗 Links │ │ │ │ ABC Company  │ │ XYZ Corp     │ │ 123 Ltd      │  │  │
│ │ 📱 Market│ │ │ │ [PROSPECT]   │ │ [DEMO]       │ │ [NEGOTIATING]│  │  │
│ │ 📚 Resources│ │ │              │ │              │ │              │  │  │
│ │          │ │ │ │ ERP + SACCO  │ │ Payroll      │ │ Full Suite   │  │  │
│ │ ACCOUNT  │ │ │ │ Est: 230K    │ │ Est: 89K     │ │ Est: 450K    │  │  │
│ │ 👤 Profile│ │ │ │              │ │              │ │              │  │  │
│ │ ⚙️ Settings│ │ │ │ [View →]     │ │ [View →]     │ │ [View →]     │  │  │
│ │ 🚪 Logout│ │ │ └──────────────┘ └──────────────┘ └──────────────┘  │  │
│ └──────────┘ │ └────────────────────────────────────────────────────────┘  │
│              │                                                              │
│              │ EARNINGS & ACTIVITY                                          │
│              │ ┌─────────────────────────┬──────────────────────────────┐  │
│              │ │ Commission Trend        │ Recent Activity              │  │
│              │ │ ─────────────────────── │ ──────────────────────────── │  │
│              │ │ [====== Chart ======]   │ • New lead: ABC Company      │  │
│              │ │                         │ • Commission paid: KES 15K   │  │
│              │ │                         │ • Demo scheduled: XYZ Corp   │  │
│              │ └─────────────────────────┴──────────────────────────────┘  │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

### 2. Enhanced Metric Cards for Resellers
```
┌─────────────────────────────────────────┐
│ ╔═══════════════════════════════════╗   │
│ ║  💰  Total Commission             ║   │
│ ╠═══════════════════════════════════╣   │
│ ║                                   ║   │
│ ║      KES 45,000                   ║   │
│ ║    ┌────────────┐                 ║   │
│ ║    │ ↑ 23.5%    │ vs last month   ║   │
│ ║    └────────────┘                 ║   │
│ ║                                   ║   │
│ ║  This Month: 5 sales closed       ║   │
│ ╚═══════════════════════════════════╝   │
│                                         │
│ Hover: View commission breakdown →      │
└─────────────────────────────────────────┘
```

### 3. Referral Pipeline Cards
```
┌──────────────────────────────────────────┐
│ ╔══════════════════════════════════════╗ │
│ ║      LEAD → DEMO → NEGOTIATING       ║ │
│ ║  ┌────┐                              ║ │
│ ║  │ 🏢 │  ABC Company Ltd             ║ │
│ ║  └────┘                              ║ │
│ ║                                      ║ │
│ ║  Products: ERP + SACCO               ║ │
│ ║  Potential: KES 230,000/year         ║ │
│ ║  Stage: Initial Contact              ║ │
│ ║  Last Contact: 2 days ago            ║ │
│ ║                                      ║ │
│ ║  Progress: [██████░░░░░░░░] 40%      ║ │
│ ║                                      ║ │
│ ║  [📞 Call] [📧 Email] [📅 Schedule]  ║ │
│ ╚══════════════════════════════════════╝ │
└──────────────────────────────────────────┘
```

### 4. Modern Sidebar Design
```
EXPANDED STATE:                    COLLAPSED:
┌─────────────────────┐           ┌────┐
│ 🚀 Evolve Reseller  │           │ 🚀 │
├─────────────────────┤           ├────┤
│ DASHBOARD           │           │    │
│ 📊 Overview     ✓   │           │ 📊 │
│                     │           │    │
│ SALES TOOLS         │           │    │
│ 🎯 Leads & Referrals│           │ 🎯 │
│ 🤝 Active Deals     │           │ 🤝 │
│ 📈 Sales Reports    │           │ 📈 │
│                     │           │    │
│ EARNINGS            │           │    │
│ 💰 Commissions      │           │ 💰 │
│ 📋 Invoices         │           │ 📋 │
│ 💳 Payout History   │           │ 💳 │
│                     │           │    │
│ MARKETING           │           │    │
│ 🔗 Referral Links   │           │ 🔗 │
│ 📱 Marketing Tools  │           │ 📱 │
│ 📚 Resources        │           │ 📚 │
│                     │           │    │
│ 👤 My Profile       │           │ 👤 │
│ ⚙️ Settings         │           │ ⚙️ │
│ 🚪 Logout          │           │ 🚪 │
└─────────────────────┘           └────┘
```

---

## 🏗️ HTML Structure & Component Architecture

### 1. Directory Structure (Reseller Module)
```
templates/dashboards/reseller/
├── layouts/
│   ├── reseller-base.html          # Base template for reseller pages ✓
│   └── includes/
│       ├── reseller-sidebar.html   # Reseller-specific sidebar ✓
│       ├── reseller-header.html    # Top navigation ✓
│       └── reseller-footer.html    # Footer ✓
├── pages/
│   ├── dashboard.html              # Main dashboard ✓
│   ├── sales/
│   │   ├── leads.html             # Lead management ✓
│   │   ├── referrals.html         # Active referrals ✓
│   │   └── reports.html           # Sales reports ✓
│   ├── earnings/
│   │   ├── commissions.html       # Commission overview ✓
│   │   ├── invoices.html          # Invoice history ✓
│   │   └── payouts.html           # Payout history ✓
│   └── marketing/
│       ├── links.html             # Referral link generator ✓
│       ├── tools.html             # Marketing materials ✓
│       └── resources.html         # Training resources ✓
└── components/
    ├── referral-card.html         # Referral pipeline card ✓
    ├── commission-card.html       # Commission metric card
    ├── activity-feed.html         # Recent activity ✓
    ├── earnings-chart.html        # Earnings visualization ✓
    └── lead-modal.html            # Add/edit lead modal

static/reseller/
├── css/
│   ├── reseller-variables.css    # Reseller theme variables ✓
│   ├── reseller-layout.css       # Layout styles ✓
│   ├── reseller-components.css   # Component styles ✓
│   ├── reseller-responsive.css   # Responsive overrides ✓
│   ├── sidebar.css               # Sidebar styles with scrollbar ✓
│   ├── reseller-base.css         # Base styles for proper scrolling ✓
│   └── dashboard-page.css        # Dashboard-specific styles ✓
├── js/
│   ├── reseller-app.js          # Main application logic ✓
│   ├── lead-manager.js          # Lead/referral management ✓
│   ├── commission-tracker.js    # Commission calculations ✓
│   ├── chart-builder.js         # Chart configurations ✓
│   └── sidebar.js               # Sidebar toggle functionality ✓
└── images/
    ├── tier-badges/             # Partnership tier badges
    └── product-icons/           # Product icons
```


---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1)
- [x] Set up reseller module directory structure
- [x] Create reseller-specific CSS variables and theme
- [x] Build base templates and layouts
- [x] Implement responsive grid system

### Phase 2: Core Components (Week 2)
- [x] Referral pipeline cards
- [x] Commission tracking cards
- [x] Enhanced sidebar navigation (with scrollbar and minimize/maximize)
- [x] Activity feed component

### Phase 3: Sales Tools (Week 3)
- [ ] Lead management interface
- [ ] Referral tracking system
- [ ] Quick action buttons
- [ ] Stage progression workflow

### Phase 4: Earnings & Reports (Week 4)
- [ ] Commission dashboard
- [ ] Invoice management
- [ ] Payout history
- [ ] Performance analytics

### Phase 5: Marketing & Resources (Week 5)
- [ ] Referral link generator
- [ ] Marketing material library
- [ ] Training resources section
- [ ] Performance optimization

---

## 🎨 Design System

### Color Usage
- **Primary Actions**: Indigo (#4f46e5)
- **Commission/Success**: Green (#10b981)
- **Pending/Warning**: Amber (#f59e0b)
- **Lost/Danger**: Red (#ef4444)
- **Backgrounds**: Gray scale (#f9fafb to #111827)

### Typography
- **Headings**: Inter, system-ui
- **Body**: Inter, system-ui
- **Numbers**: 'Roboto Mono', monospace

### Tier System Colors
- Bronze: #cd7f32
- Silver: #c0c0c0
- Gold: #ffd700
- Platinum: #e5e4e2

### Component States
- Default
- Hover
- Active
- Focus
- Disabled
- Loading

---

## 📝 Key Features to Implement

1. **Referral Pipeline Management**
   - Visual pipeline with drag-and-drop
   - Stage progression tracking
   - Automated follow-up reminders
   - Quick actions for communication

2. **Commission Tracking**
   - Real-time commission calculations
   - Detailed breakdown by product
   - Payment history
   - Tier progression tracking

3. **Lead Management**
   - Lead capture forms
   - Lead scoring system
   - Activity tracking
   - Conversion analytics

4. **Marketing Tools**
   - Custom referral link generator
   - QR codes for events
   - Email templates
   - Social media assets

5. **Performance Analytics**
   - Conversion rate tracking
   - Revenue attribution
   - Comparative analysis
   - Goal setting and tracking

6. **Mobile Experience**
   - Responsive design
   - Touch-optimized interfaces
   - Offline capability
   - Push notifications

This plan creates a comprehensive, modern reseller dashboard that empowers partners to effectively sell Lixnet's products and track their performance.

---

## 📋 Completed Features (Phase 1 & 2)

### Sidebar Enhancements
1. **Scrollable Sidebar**
   - Added custom scrollbar for sidebar navigation
   - Scrollbar appears when content exceeds viewport height
   - Smooth scrolling with webkit and Firefox support
   - Sidebar remains fixed while main content scrolls

2. **Collapsible Sidebar**
   - Toggle button to minimize/maximize sidebar
   - Collapsed state shows only icons
   - Tooltips on hover when collapsed
   - State persists using localStorage
   - Smooth transitions between states

3. **Visual Improvements**
   - Changed from dark theme to blue theme (#2563eb)
   - Enhanced hover and active states
   - Removed duplicate hamburger menu from header
   - Added shadow for better separation
   - Improved button styling with better visibility

4. **Technical Implementation**
   - Created `sidebar.css` for all sidebar styles
   - Created `sidebar.js` for toggle functionality
   - Added `reseller-base.css` for proper layout structure
   - Fixed z-index layering between header and sidebar
   - Ensured proper height calculations (100vh - 60px header)
