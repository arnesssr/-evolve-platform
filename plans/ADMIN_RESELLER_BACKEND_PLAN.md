# Admin Reseller Backend Plan (Option A)

Status: Draft (Option A approved)
Owner: Admin Module
Scope: Implement admin-facing backend for Resellers with strict Separation of Concerns (SoC), reusing domain logic from App/reseller/…

---

## 1) Goals and Constraints
- Provide admin UI data and actions for Resellers (list, filters, metrics, detail, edit, bulk actions, payouts, export, messaging) strictly via the Admin layering.
- Do NOT place domain logic in Admin. Admin orchestrates; domain (App/reseller/…) contains business rules and writes.
- Preserve template URL expectations (namespace: `platform_admin`).
- Keep views thin (HTTP only), forms for validation, services for orchestration, repositories for read-optimized queries, utils for helpers.

---

## 2) Templates/Features Covered (from templates/dashboards/admin/pages/resellers)
- list.html
  - Top metrics: total resellers, active resellers, total commission, top performer
  - Filters: text search, performance, commission tier, registration date range
  - Table: identity, performance, commission tier, total earnings, sales count, status, joined, actions (view/edit/suspend/delete…)
  - Bulk actions (modal), quick create (modal), export, pagination
- detail.html
  - Profile + metrics: total earnings, sales count, conversion rate, commission rate, avg deal size
  - Commission summary: pending, monthly, yearly
  - Sales performance chart (Chart.js), recent sales list
  - Recent activity timeline
  - Account info: joined, last login, referral code, territory
  - Actions: process payout, suspend account, send message, edit reseller

---

## 3) Directory and Files to Add (Option A)

### URLs
- App/admin/urls/resellers.py
  - app_name = 'platform_admin' (share namespace)
  - URL names:
    - resellers-list (GET)
    - resellers-detail (GET)
    - resellers-export (GET CSV)
    - resellers-bulk (POST)
    - reseller-create (POST)
    - reseller-edit (POST)
    - reseller-suspend (POST)
    - reseller-resume (POST)
    - reseller-payout (POST)
    - reseller-message (POST)
    - reseller-stats (GET JSON for charts)
- App/admin/urls.py
  - Include the above module and keep existing names working (preserve `platform_admin` namespace).

### Views (HTTP, thin controllers)
- App/admin/views/resellers.py
  - AdminResellerListView (GET)
  - AdminResellerDetailView (GET)
  - AdminResellerExportView (GET CSV)
  - AdminResellerBulkActionView (POST)
  - AdminResellerCreateView (POST)
  - AdminResellerEditView (POST)
  - AdminResellerSuspendView/AdminResellerResumeView (POST)
  - AdminResellerPayoutView (POST)
  - AdminResellerMessageView (POST)

### Forms (validation only)
- App/admin/forms/resellers.py
  - ResellerFilterForm: q, performance, commission_tier, status, joined_from, joined_to, page, page_size
  - ResellerCreateForm: name, email, phone, company, tier, territory, specialization, status
  - ResellerEditForm: same as create (all optional), reseller_id
  - ResellerBulkActionForm: action in {suspend,resume,delete,set_tier,message}, reseller_ids[], tier?, message?
  - PayoutForm: reseller_id, amount?, period?, payout_type
  - MessageForm: reseller_id(s), channel in {email,sms}, subject?, body

### Services (admin orchestration; no request/response objects)
- App/admin/services/resellers_service.py
  - list_resellers(filters, pagination) -> PagedResult[ResellerListRow]
  - compute_metrics() -> {total_resellers, active_resellers, total_commission, top_performer}
  - get_reseller_detail(reseller_id) -> ResellerDetailVM
  - create_reseller(data) -> reseller_id
  - update_reseller(reseller_id, data)
  - suspend_reseller(reseller_id, reason?)
  - resume_reseller(reseller_id)
  - process_payout(reseller_id, params) -> payout_id/status
  - send_message(reseller_ids, channel, payload)
  - export_rows(filters) -> iterator/rows (consumed by utils.csv)
  Notes:
  - Delegate write operations to domain (App/reseller/earnings/services, repositories, etc.).
  - Aggregate read models possibly via admin repositories (below).

### Repositories (read-optimized queries and aggregates)
- App/admin/repositories/resellers_repository.py
  - query_resellers(filters, order, pagination) -> queryset or list[ResellerListRow]
  - compute_admin_metrics() -> totals for list header
  - get_reseller_overview(reseller_id) -> profile + aggregates
  - get_reseller_sales(reseller_id, range?) -> list/sum for recent sales table
  - get_commission_summary(reseller_id) -> pending, monthly, yearly
  - get_activity_timeline(reseller_id) -> recent activity items
  - get_chart_series(reseller_id, months=12) -> timeseries for Chart.js

### API (optional initially; enables server-side DataTables and Chart data)
- App/admin/api/v1/views/resellers.py
  - GET /platform-admin/api/v1/resellers/ (filters, pagination)
  - GET /platform-admin/api/v1/resellers/{id}/
  - GET /platform-admin/api/v1/resellers/{id}/stats
  - POST /platform-admin/api/v1/resellers/bulk
  - POST /platform-admin/api/v1/resellers/{id}/payout
  - POST /platform-admin/api/v1/resellers/{id}/suspend|resume
  - POST /platform-admin/api/v1/resellers/{id}/message
- App/admin/api/v1/serializers/resellers.py
  - ResellerListSerializer, ResellerDetailSerializer, ResellerStatsSerializer, BulkActionSerializer

### Utils and Exceptions
- App/admin/utils/data_export.py (reuse) or utils/resellers_export.py
  - export_resellers_to_csv(rows, response)
- App/admin/exceptions/admin_exceptions.py (extend)
  - ResellerNotFound, InvalidBulkAction, PayoutFailure, PermissionDenied
- App/admin/permissions.py
  - AdminRequiredMixin/Decorator (staff/is_admin) for all views

### Tests
- App/admin/tests/test_views/test_resellers.py
- App/admin/tests/test_services/test_resellers_service.py
- App/admin/tests/test_api/test_resellers_api.py

---

## 4) URL Map → Template Pages
- GET platform_admin:resellers-list → templates/dashboards/admin/pages/resellers/list.html
  - Query params: q, performance, commission_tier, status, joined_from, joined_to, page
  - Provides metrics and table rows via context.
- GET platform_admin:resellers-detail (id) → templates/dashboards/admin/pages/resellers/detail.html
  - Provides profile, metrics, recent sales, commission summary, activity, chart series.
- GET platform_admin:resellers-export → CSV download for current filters.
- POST platform_admin:resellers-bulk → bulk suspend/resume/delete/set_tier/message.
- POST platform_admin:reseller-create → quick-create modal submit.
- POST platform_admin:reseller-edit → edit modal submit.
- POST platform_admin:reseller-payout → process payout from detail page.
- POST platform_admin:reseller-suspend/resume → toggle status.
- POST platform_admin:reseller-message → send email/SMS.
- GET platform_admin:reseller-stats → JSON for Chart.js (optional).

---

## 5) Data Contracts (Admin-side View Models)

### ResellerListRow
- id, name, email, company
- performance_segment (Excellent/Good/… + score%)
- commission_tier (Premium/Standard/Basic + %)
- total_earnings (decimal)
- sales_count (int), sales_this_month (int)
- status (active/suspended/pending)
- joined_at (datetime)

### ResellerDetailVM
- profile: id, name, email, phone, company, specialization, territory, website, status, tier, referral_code, join_date, last_login
- metrics: sales_count, conversion_rate, commission_rate, avg_deal_size, total_earnings
- commission_summary: pending, monthly, yearly
- recent_sales: [{business, plan, amount, commission, date, status}, …]
- activity_timeline: [{ts, type, text}], recent first
- chart_series: timeseries (label -> value), last 12 months

---

## 6) SoC Rules (Enforced)
- Views: HTTP only (params, auth, rendering, redirects). No ORM or domain writes.
- Forms: validation only; return cleaned_data.
- Services: orchestrate; call domain services for mutations; call admin repositories for read models; no request/response.
- Repositories: read-only aggregates/joins optimized for admin reporting.
- API: JSON controllers only; reuse services.
- Utils: pure helpers (e.g., CSV). No business logic.
- Exceptions: typed errors for consistent handling.
- Admin never imported by domain; domain never depends on admin.

---

## 7) Security and Auditing
- Decorate all admin views with LoginRequired + Admin permission check.
- CSRF protection on all POST endpoints.
- Audit log entries for: create/edit, suspend/resume, payouts, bulk actions, messages.
- Rate-limit sensitive actions (optional).

---

## 8) Rollout Steps
1. Scaffold files: urls/resellers.py, views/resellers.py, forms/resellers.py, services/resellers_service.py, repositories/resellers_repository.py, api/v1/views+serializers.
2. Wire urls.py to include resellers routes under namespace `platform_admin`.
3. Implement list view with filters + metrics (read-only).
4. Implement create/edit + bulk actions (POST; stub domain calls if needed).
5. Implement detail view + stats + recent sales + commission summary.
6. Implement payouts/suspend/resume/messaging actions.
7. Implement CSV export.
8. Add tests for services and views; add API tests if API enabled.

---

## 9) Dependencies and Integration Points
- Domain services: App/reseller/earnings/services, App/reseller/... repositories/models.
- Email/SMS: use configured EMAIL_* and SMS providers.
- Chart.js: provide series via context or JSON endpoint.

---

## 10) Open Questions
- Server-side DataTables now or later? (Initial plan: client-side; optional API later.)
- Payout processing sync vs async (Celery) for larger volumes?
- Messaging scope: email only or email+SMS?

