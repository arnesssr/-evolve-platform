# Reseller Marketing UI Cleanup Plan (MVP)
Date: 2025-08-29
Owner: Agent Mode

Objective
- Remove UI noise to focus the reseller experience on generating a real referral link, sharing it, and seeing clicks/conversions that map to commissions.

In Scope (now)
- Hide/remove Marketing > Tools and Marketing > Resources from navigation (desktop & mobile).
- Trim Marketing > Links to a minimal, wire-ready form and list.
- Remove QR code and link shortener UI and any fake link generation logic.

Out of Scope (now)
- Backend wiring to actual link generation endpoints.
- Deleting backend models/APIs for tools/resources (only hiding from UI for now).
- Implementing QR code or shortening.

Files to change and what we’ll do
1) templates/dashboards/reseller/layouts/includes/reseller-sidebar.html
   - Remove the Tools and Resources navigation items under the “Marketing” group.

2) templates/dashboards/reseller/layouts/includes/mobile-navigation.html
   - Remove Tools and Resources items in the Mobile Menu Offcanvas under “Marketing”.
   - Update the bottom-nav Marketing active-state to no longer consider 'tools'.

3) templates/dashboards/reseller/pages/marketing/links.html
   - Remove the following inputs from the form: UTM Source, Landing Page, Custom Parameters.
   - Remove QR code button, Shorten Link button, and the QR Code modal.
   - Remove hardcoded (fake) client-side link generation; keep a placeholder submit handler.
   - Update copy-to-clipboard to use navigator.clipboard (no execCommand).
   - Keep the Active Links table and the single Copy action. Optionally keep View stats if route exists.

Rationale
- Keeps UI focused on the link → click → conversion → commission funnel.
- Eliminates features that require extra content, assets, or plumbing and don’t affect the MVP flow.
- Avoids fake behavior that can confuse users (e.g., hardcoded links, non-functional QR/shorten).

Acceptance Criteria
- Desktop sidebar shows only Marketing > Links (no Tools/Resources).
- Mobile navigation (offcanvas) shows only Marketing > Links.
- Links page has:
  - Form fields: Campaign Name, Product, Generate button.
  - Generated Link section (hidden until wired), retains Copy button.
  - No UTM Source, Landing Page, or Custom Params fields.
  - No QR/Shorten buttons and no QR modal.
  - No fake link generation in JS.

Rollback
- Re-add the removed navigation blocks in the sidebar and mobile navigation files.
- Restore removed HTML blocks in links.html if needed from VCS history.

Next Steps (wiring)
- Wire POST /reseller/links (or existing endpoint) to generate a short code and return short_url.
- On success, set #generatedLink value and reveal #generatedLinkSection.
- Ensure click resolver route /r/:code records click and redirects.
- Ensure Pesapal webhook updates commissions exactly once per paid order.
- Populate Product select from server-side context or a lightweight API.

