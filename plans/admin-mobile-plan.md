# Admin Mobile UX Parity Plan

Objective
- Bring the Admin dashboard mobile UX to parity with the Reseller dashboard: remove sidebar traces on small screens, add a mobile bottom navigation, ensure header icons don’t overlap, and use a Facebook-like system font stack on mobile (native OS fonts).

Scope
- Affects all Admin dashboard templates under templates/dashboards/admin and supporting CSS/JS under static.
- Non-admin (marketing/landing/auth) are out-of-scope for this plan.

Current State (Admin)
- Base: templates/dashboards/admin/layouts/admin-base.html
  - Sidebar: fixed on desktop; off-canvas on mobile via transform translateX(-100%) and an overlay.
  - Main: margin-left and width based on sidebar width; resets to 0/100% on mobile.
  - Header: sticky 70px, contains a sidebar toggle and two buttons.
  - No bottom mobile navigation present.
  - Body font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif.
- Includes present: admin-header.html, admin-sidebar.html

Gap Analysis vs Reseller Mobile UX
- Missing bottom mobile nav for quick access to key sections.
- No explicit mobile system-font override across all admin components.
- Need explicit padding-bottom for content so it doesn’t sit under new bottom nav.
- Ensure header controls (buttons/dropdowns) don’t overlap on mobile.
- Ensure no residual “sidebar traces” (spacing/gaps) on mobile; admin-main margin-left resets on mobile, so mostly OK, but we’ll guard with stronger selectors as in reseller.

Work Plan
1) Introduce Admin mobile CSS
   - Create static/admin/css/mobile-navigation.css with:
     - Bottom nav styles (mirroring reseller), offcanvas for “More”.
     - Sidebar suppression/spacing fixes on mobile.
     - Content padding-bottom for bottom nav.
     - Mobile header adjustments (56px, compact controls).
     - System font stack override on mobile only.

2) Add Admin mobile bottom navigation include
   - Create templates/dashboards/admin/layouts/includes/mobile-navigation.html.
   - Items: Home (dashboard), Businesses, Financial, Reports, More (offcanvas with grid for Admins, Products, Resellers, Analytics, Settings, System, Logout).

3) Wire into base layout
   - In admin-base.html <head>, link the new mobile-navigation.css after existing CSS.
   - After .admin-wrapper, include the mobile-navigation.html.

4) Sidebar traces and layout guards
   - In the mobile CSS, force .admin-main and .admin-content to full width with margin-left: 0 on mobile, including collapsed/expanded variations.
   - Keep overlay/show behavior for the sidebar toggle on mobile; ensure no unintended gaps.

5) Mobile header compactness
   - Ensure the sidebar toggle is visible on mobile.
   - Keep a compact title; ensure right-side controls fit without overlap.

6) Typography
   - On mobile (<= 991.98px), force a system font stack across body and common interactive elements (buttons, inputs, menus, modals).

7) QA and Acceptance
   - Manually test on iOS Safari and Android Chrome (DevTools emulation acceptable).
   - Validate:
     - Sidebar never leaves left gaps on mobile.
     - Bottom nav is visible and usable across admin pages.
     - Header icons and dropdowns do not overlap or overflow.
     - Content scrolls correctly with adequate padding for fixed header and bottom nav.
     - Fonts on mobile reflect the system UI stack.

Acceptance Criteria
- On screens < 992px wide:
  - Admin sidebar is not visible by default and does not create left spacing.
  - A bottom nav is present and functional.
  - Header shows no overlapping of notification/profile/settings/logout controls.
  - Admin content has padding-top for header and padding-bottom for bottom nav.
  - Computed font-family on body is a system stack (e.g., -apple-system or Roboto).

Files to Add/Update
- Add: static/admin/css/mobile-navigation.css
- Add: templates/dashboards/admin/layouts/includes/mobile-navigation.html
- Update: templates/dashboards/admin/layouts/admin-base.html (link new CSS; include bottom nav)

Rollout
- Local/dev test → collectstatic (if applicable) → deploy.
- Monitor for layout regressions on tablet/desktop.

Notes
- We intentionally avoid introducing new icon packs; we reuse Font Awesome already present.
- If a global mobile typography override is desired platform-wide, consider a shared mobile-typography.css loaded in all base templates.

