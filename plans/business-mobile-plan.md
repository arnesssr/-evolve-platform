# Business Mobile UX Parity Plan

Objective
- Bring Business dashboard mobile UX to parity with Reseller/Admin: bottom navigation on phones, no hamburger toggle on mobile, compact typography/buttons, off-canvas sidebar only on mobile, robust desktop sidebar handling, and content spacing that avoids overlap.

Scope
- Templates under templates/dashboards/business.
- New mobile CSS under static/business/css.
- No functional changes to business logic.

Current State (Business)
- Base: templates/dashboards/business/layouts/business-base.html
  - Sidebar: fixed on desktop; CSS translates off-canvas on mobile with .show class.
  - Header: has a bars button (id=sidebar-toggle) calling toggleSidebar().
  - Main content margin controlled by inline <style> in base.
  - No bottom navigation or mobile-only typography/buttons.

Plan
1) Add mobile CSS for Business
   - static/business/css/mobile-navigation.css with:
     - System UI font stack (Facebook-like) for mobile.
     - Compact button sizing on mobile.
     - Bottom nav bar + offcanvas "More" menu.
     - Hide hamburger toggle on mobile.
     - Ensure main content has top/bottom padding for header + bottom nav.

2) Add bottom navigation include
   - templates/dashboards/business/layouts/includes/mobile-navigation.html with Home, Subscriptions, Billing, Users, Support, and More menu.

3) Wire into base layout
   - Link the new mobile CSS after existing CSS in business-base.html.
   - Include mobile-navigation.html after the wrapper.

4) Sidebar robustness on desktop
   - Ensure main content margin-left accounts for sidebar width on desktop.
   - Keep existing off-canvas behavior on mobile.

5) Typography & components
   - Shrink page header titles and labels on small screens; compact card paddings.

6) QA
   - Test dashboard, my-plans, software-hub, billing-history, support-center, user-management on phones: no hamburger, bottom nav visible, no content hidden behind header/nav, buttons compact.

Acceptance Criteria
- On < 992px: no hamburger; bottom nav visible; content spaced; buttons compact; system font stack active.
- On >= 992px: sidebar visible; main content margin accounts for sidebar; existing features work.

