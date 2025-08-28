# Business Dashboard MVP Trim Plan

This plan identifies non-essential UI for the Business dashboard MVP, removes obvious repetitions, and specifies targeted edits. The goal is to ship a lean, functional dashboard focused on core customer tasks: access software, manage subscriptions, view invoices, manage users, and get support.

Scope: templates/dashboards/business

Global changes
- Remove Chart.js and any chart widgets across pages for MVP.
- Remove the Notifications dropdown in the header (static demo content; requires backend to be meaningful).
- Remove Account Settings link from header and sidebar (no implemented page).
- Remove Quick Launch block from the sidebar (duplicated with Dashboard/Software Hub).
- Fix software tile include param naming: use launch_url consistently in page includes.
- Remove duplicate template: business-dashboard.html (keep pages/dashboard.html as the single Dashboard page).

Per-page changes
1) Dashboard (pages/dashboard.html)
- Keep: Welcome card; Quick Stats; Active Software tiles grid; Quick Actions.
- Remove: Usage Overview doughnut chart and its extra_js.
- Improve: Fix software tile include to pass launch_url instead of url.

2) Software Hub (pages/software-hub.html)
- Keep: Your Licensed Software; Trial Software.
- Remove: Available Software (marketplace promotions); Quick Stats; System Status; Recent Updates; purchase/upgrade modals and related JS.
- Rationale: Business users primarily launch owned/trial software; marketplace belongs elsewhere.

3) Subscriptions (pages/my-plans.html)
- Keep: Three subscription cards; Cost Summary; Next Renewals.
- Remove: Usage Analytics chart; Upgrade modal; extra_js.
- Rationale: MVP shows current plan state and renewal info; upgrades can be a link later.

4) Billing & Invoices (pages/billing-history.html)
- Keep: Invoices table; Payment Method card; Billing Information card.
- Remove: Top metric cards row; Payment Method modal (placeholder without backend).

5) User Management (pages/user-management.html)
- Keep: Users table; Add User modal; filtering controls.
- Remove: Top User Stats metric cards.

6) Support Center (pages/support-center.html)
- Keep: New Ticket button + modal; Contact Information card.
- Remove: Quick Action cards; Tickets table; Support Hours card.
- Rationale: MVP offers simple contact/ticket submission; lists/filters require backend.

Implementation checklist
- layouts/business-base.html: remove Chart.js include.
- layouts/includes/business-header.html: remove Notifications dropdown; remove Account Settings item.
- layouts/includes/business-sidebar.html: remove Quick Launch block; remove Settings nav item.
- pages/dashboard.html: delete Usage Overview card + JS; fix software tile includes to use launch_url.
- pages/software-hub.html: delete Marketplace, Quick Stats, System Status, Recent Updates, modals, and JS.
- pages/my-plans.html: delete Usage Analytics card, Upgrade modal, extra_js block.
- pages/billing-history.html: delete top summary row; delete Payment Method modal.
- pages/support-center.html: delete Quick Actions row; Tickets table; Support Hours card.
- pages/user-management.html: delete top User Stats cards.
- Remove templates/dashboards/business/business-dashboard.html (duplicate of pages/dashboard.html).

Post-change sanity
- All templates still extend layouts/business-base.html and render without Chart.js.
- Sidebar contains only live pages: Dashboard, Software Hub, Subscriptions, Billing & Invoices, User Management, Support Center.
- Header dropdown contains Support, Billing & Invoices, Logout.
- Software tiles launch buttons work (use launch_url).

