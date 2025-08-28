# Plan: Remove stat cards from reseller pages

Targeted pages and sections to remove:
1) Earnings > Invoices (templates/dashboards/reseller/pages/earnings/invoices.html)
   - Section: "Invoice Summary Cards" row containing 4 .stat-card cards.
2) Earnings > Payouts (templates/dashboards/reseller/pages/earnings/payouts.html)
   - Section: "Key Stats" row containing 4 .stat-card cards.
3) Marketing > Tools (templates/dashboards/reseller/pages/marketing/tools.html)
   - Section: "Quick Stats" row containing 4 .stat-card cards.
4) Sales > Leads (templates/dashboards/reseller/pages/sales/leads.html)
   - Section: "Lead Statistics" row containing 4 .stat-card cards.
5) Sales > Referrals (templates/dashboards/reseller/pages/sales/referrals.html)
   - Section: "Quick Stats" row containing 4 .stat-card cards.
6) Earnings > Commissions (templates/dashboards/reseller/pages/earnings/commissions.html)
   - Section: Commission Stats row with 4 .stat-card.stat-card-square tiles.

Rationale
- These stat cards duplicate information shown elsewhere or add visual clutter without actionable controls. Removing them simplifies the UI and emphasizes core tasks and data tables.

Approach
- Delete the exact rows/div blocks containing .stat-card sections, keeping surrounding filters, tables, and charts intact.
- Verify that grid spacing remains coherent after removal.

Risks
- Users may rely on quick at-a-glance metrics. If needed, we can reintroduce a minimal header KPI in the future with better context/actions.

