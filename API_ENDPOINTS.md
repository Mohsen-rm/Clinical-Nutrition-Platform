# API Endpoints

All backend endpoints are namespaced under the base path: `http://<BACKEND_HOST>/api/`

- Admin panel: `http://<BACKEND_HOST>/admin/`

Replace `<BACKEND_HOST>` with your backend host (e.g., `127.0.0.1:8000`).

---

## Auth (`/api/auth/`)

- `POST /api/auth/register/`
  - Create a new user account. Returns user data and JWT tokens.
- `POST /api/auth/login/`
  - Login with email/password. Returns user data and JWT tokens.
- `POST /api/auth/logout/`
  - Logout current session. Optionally blacklists refresh token if provided.
- `GET /api/auth/profile/`
  - Get current authenticated user profile.
- `PUT /api/auth/profile/`
  - Update current authenticated user profile.
- `POST /api/auth/change-password/`
  - Change current user's password.
- `POST /api/auth/token/refresh/`
  - Refresh access token using refresh token.
- `GET /api/auth/referral/<code>/`
  - Validate a referral code. Returns referrer info if valid.

---

## Subscriptions (`/api/subscriptions/`)

- `GET /api/subscriptions/plans/`
  - List active subscription plans.
- `POST /api/subscriptions/create/`
  - Create a subscription with `plan_id` and `payment_method_id`.
- `GET /api/subscriptions/status/`
  - Get current user's subscription status/details.
- `POST /api/subscriptions/cancel/`
  - Cancel subscription (supports `cancel_at_period_end`).
- `POST /api/subscriptions/payment-intent/`
  - Create a Stripe Payment Intent for one-off flows (amount derived from plan).
- `POST /api/subscriptions/webhook/`
  - Stripe webhook endpoint (Stripe calls this). Requires `STRIPE_WEBHOOK_SECRET`.

---

## Affiliates (`/api/affiliates/`)

- `GET /api/affiliates/stats/`
  - Get affiliate statistics for the current user.
- `GET /api/affiliates/commissions/`
  - List commission history. Supports `?status=pending|paid`, `?page=`, `?page_size=`.
- `GET /api/affiliates/referrals/`
  - List users referred by the current user with subscription info.
- `GET /api/affiliates/payouts/`
  - List payout requests for the current user.
- `POST /api/affiliates/payouts/`
  - Create a new payout request.
- `POST /api/affiliates/generate-link/`
  - Generate or refresh your affiliate link (`/register?ref=<CODE>`).
- `GET /api/affiliates/dashboard/`
  - Aggregated dashboard data (earnings, referrals, recent items).

---

## Nutrition (`/api/nutrition/`)

- `GET /api/nutrition/diseases/`
  - List all diseases and dietary notes.
- `GET /api/nutrition/plans/`
  - List nutrition plans for the current user.
- `POST /api/nutrition/plans/`
  - Create a new nutrition plan. Supports `disease_ids` or `diseases` array.
- `GET /api/nutrition/plans/<plan_id>/`
  - Get details of a specific plan (doctor or owning patient only).
- `PUT /api/nutrition/plans/<plan_id>/`
  - Update a nutrition plan (doctor or owning patient only).
- `POST /api/nutrition/calculate/`
  - Calculate BMR/TDEE/targets without saving a plan.
- `GET /api/nutrition/whatsapp/`
  - List WhatsApp messages (demo storage).
- `POST /api/nutrition/whatsapp/`
  - Send a WhatsApp message (demo; stores and auto-replies).
- `GET /api/nutrition/demo/`
  - Demo endpoint showing disease-calorie logic.

---

## Notes

- All authenticated endpoints require `Authorization: Bearer <access_token>`.
- Pagination and filters are indicated where applicable.
- Stripe keys and webhook secret must be configured via environment variables.
- For full request/response schemas, refer to serializers and views under:
  - `backend/apps/accounts/`
  - `backend/apps/subscriptions/`
  - `backend/apps/affiliates/`
  - `backend/apps/nutrition/`
