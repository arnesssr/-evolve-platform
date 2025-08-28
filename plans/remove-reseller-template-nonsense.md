# Plan: Remove nonsensical/unhelpful elements from reseller templates

Goal
- Clean up reseller-related templates by removing placeholder UI, dead links, duplicate or broken script includes, and debug artifacts that don’t provide user value.

Scope
- templates/dashboards/reseller/reseller-dashboard.html
- templates/dashboards/reseller/pages/dashboard.html
- templates/dashboards/reseller/components/activity-feed.html
- templates/dashboards/reseller/components/lead-modal.html
- templates/dashboards/reseller/layouts/includes/reseller-header.html
- templates/dashboards/reseller/layouts/includes/reseller-footer.html
- templates/dashboards/reseller/pages/marketing/resources.html
- templates/dashboards/reseller/pages/sales/referrals.html
- templates/dashboards/reseller/pages/sales/reports.html
- templates/dashboards/reseller/pages/earnings/payouts.html
- templates/dashboards/admin/pages/resellers/detail.html

Changes by file
1) reseller-dashboard.html
- Remove static toast element (✔ Commission Paid Successfully)
- Remove duplicate/unnecessary scripts in extra_js: Chart.js CDN, reseller-app.js, chart-builder.js, charts.js, toasts.js
- Remove inline initializer relying on undefined functions

2) pages/dashboard.html
- Remove duplicate/unnecessary scripts in extra_js: reseller-app.js, chart-builder.js

3) components/activity-feed.html
- Remove “View All” link pointing to # (dead link)

4) components/lead-modal.html
- Remove console.log debug statement in saveLead()

5) layouts/includes/reseller-header.html
- Remove static notification badge “3” (hardcoded)
- Remove Help link pointing to # (dead link)

6) layouts/includes/reseller-footer.html
- Remove social links block with href="#" (LinkedIn/Twitter/YouTube dead links)

7) pages/marketing/resources.html
- Remove dead links: “View All Webinars”, “Browse All Courses”, “Explore All Services” (href="#")

8) pages/sales/referrals.html
- Remove static text “Industry avg: 25%”

9) pages/sales/reports.html
- Remove export buttons that call undefined exportReport('pdf'|'excel')

10) pages/earnings/payouts.html
- Remove console.log debug statements

11) admin/pages/resellers/detail.html
- Remove “View All” link (href="#") from Recent Sales header
- Remove “Send Message” menu item (href="#")
- Remove static “Premium Tier” badge

Rationale
- Dead links (#) confuse users and should not appear in production.
- Duplicate/broken script includes can cause runtime errors and performance issues.
- Hardcoded badges and debug toasts mislead users.
- Console logs are noisy in production templates.

Risks and mitigations
- Minor styling/behavior changes due to removing toasts, badges, or links. Mitigated by keeping core functionality intact and only deleting non-functional placeholders.
- If any page relied on removed scripts, the base layout still provides Chart.js and core scripts. We are only removing duplicate/broken ones.

Verification
- Render key pages to ensure no JS console errors from removed scripts.
- Spot-check headers/footers to ensure layout intact.

