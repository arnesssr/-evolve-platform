# Plan: Refine Reseller UI for a professional, consistent look

Goal
- Make all reseller pages visually consistent and professional with a clear layout hierarchy, consistent headers, spacing, and card styles using Bootstrap 5 + a small shared CSS layer.

Global approach
- Add a shared stylesheet (ui-standards.css) that standardizes:
  - Page headers (title/subtitle/action alignment)
  - Card radius, borders, spacing
  - Stat cards (used across earnings, marketing, sales pages)
  - Progress thickness helpers (thin/large)
  - Icon circle helpers to avoid inline width/height
- Include ui-standards.css in the reseller base so all pages inherit improvements.

Pages and concrete actions
1) Dashboard (templates/dashboards/reseller/pages/dashboard.html)
- Replace ad-hoc welcome block with standardized .page-header (title + subtitle)
- Keep existing metrics grid, charts, and activity feed; benefits from shared styles

2) Alternate dashboard (templates/dashboards/reseller/reseller-dashboard.html)
- Add standardized .page-header at the top of content
- Remove redundant extra_js (already done in previous cleanup) and rely on base scripts

3) Commission card component (templates/dashboards/reseller/components/commission-card.html)
- Remove component-local inline <style> block
- Use shared card styling from ui-standards.css

4) Reports (templates/dashboards/reseller/pages/sales/reports.html)
- Keep structure; shared CSS improves table headers and card presentation
- Optional: Replace inline progress height with CSS helpers in a follow-up

5) Invoices, Payouts, Links, Tools, Resources, Leads, Referrals, Profile pages
- No structural changes needed; they already use common classes (stat-card, card). They benefit from the shared CSS for consistent look and spacing.

Risks & mitigations
- Minimal: shared CSS could slightly change spacing/rounding; mitigated by using subtle, standard values.

Verification
- Render dashboard, earnings, marketing, sales, and profile pages to confirm consistent header spacing, card rounding, and typography.

