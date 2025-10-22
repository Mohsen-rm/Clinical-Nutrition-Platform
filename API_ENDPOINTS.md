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

---

## Examples

Below are concise JSON request/response samples for common endpoints. Ensure you send `Authorization: Bearer <access_token>` for protected routes.

### Auth

- POST `/api/auth/register/`

Request
```json
{
  "email": "doctor@example.com",
  "password": "doctor123",
  "password_confirm": "doctor123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "doctor",
  "phone_number": "+15555550123",
  "referral_code": "0E93C3E5"
}
```

Response
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 12,
    "username": "doctor",
    "email": "doctor@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "doctor",
    "phone_number": "+15555550123",
    "is_verified": false,
    "referral_code": "92820A83",
    "created_at": "2025-10-22T00:18:45.123Z",
    "profile": {"bio": null, "avatar": null, "date_of_birth": null, "license_number": null, "specialization": null, "height": null, "weight": null, "medical_conditions": null}
  },
  "tokens": {"refresh": "<refresh>", "access": "<access>"}
}
```

- POST `/api/auth/login/`

Request
```json
{"email": "doctor@example.com", "password": "doctor123"}
```

Response
```json
{
  "message": "Login successful",
  "user": {"id": 1, "username": "doctor", "email": "doctor@example.com", "first_name": "John", "last_name": "Doe", "user_type": "doctor", "phone_number": "+15555550123", "is_verified": false, "referral_code": "818FBFD2", "created_at": "2025-09-01T10:00:00Z", "profile": {...}},
  "tokens": {"refresh": "<refresh>", "access": "<access>"}
}
```

- POST `/api/auth/token/refresh/`

Request
```json
{"refresh": "<refresh>"}
```

Response
```json
{"access": "<new_access>"}
```

- GET `/api/auth/profile/` (Response)
```json
{"user": {"id": 1, "username": "doctor", "email": "doctor@example.com", "first_name": "John", "last_name": "Doe", "user_type": "doctor", "phone_number": "+15555550123", "is_verified": false, "referral_code": "818FBFD2", "created_at": "2025-09-01T10:00:00Z", "profile": {...}}}
```

### Subscriptions

- GET `/api/subscriptions/plans/` (Response)
```json
{
  "plans": [
    {"id": 1, "name": "Basic", "description": "For starters", "price": "29.00", "currency": "USD", "plan_type": "basic", "features": ["Feature A", "Feature B"], "is_active": true},
    {"id": 2, "name": "Professional", "description": "For pros", "price": "79.00", "currency": "USD", "plan_type": "professional", "features": ["Feature X", "Feature Y"], "is_active": true}
  ]
}
```

- POST `/api/subscriptions/create/`

Request
```json
{"plan_id": 2, "payment_method_id": "pm_1Nz..."}
```

Response
```json
{
  "message": "Subscription created successfully",
  "subscription": {
    "id": 5,
    "plan": {"id": 2, "name": "Professional", "description": "For pros", "price": "79.00", "currency": "USD", "plan_type": "professional", "features": ["Feature X", "Feature Y"], "is_active": true},
    "plan_id": 2,
    "plan_name": "Professional",
    "amount": 7900,
    "status": "active",
    "current_period_start": "2025-10-22T00:20:10.000Z",
    "current_period_end": "2025-11-21T00:20:10.000Z",
    "cancel_at_period_end": false,
    "canceled_at": null,
    "days_until_renewal": 30,
    "is_active": true,
    "created_at": "2025-10-22T00:20:11.000Z"
  },
  "client_secret": null
}
```

- GET `/api/subscriptions/status/` (Response)
```json
{
  "subscription": {
    "id": 5,
    "plan": {"id": 2, "name": "Professional", "description": "For pros", "price": "79.00", "currency": "USD", "plan_type": "professional", "features": ["Feature X", "Feature Y"], "is_active": true},
    "plan_id": 2,
    "plan_name": "Professional",
    "amount": 7900,
    "status": "active",
    "current_period_start": "2025-10-22T00:20:10.000Z",
    "current_period_end": "2025-11-21T00:20:10.000Z",
    "cancel_at_period_end": false,
    "canceled_at": null,
    "days_until_renewal": 30,
    "is_active": true,
    "created_at": "2025-10-22T00:20:11.000Z"
  }
}
```

- POST `/api/subscriptions/cancel/`

Request
```json
{"cancel_at_period_end": true}
```

Response
```json
{"message": "Subscription canceled successfully", "subscription": {"id": 5, "cancel_at_period_end": true, "status": "active", "current_period_end": "2025-11-21T00:20:10.000Z"}}
```

- POST `/api/subscriptions/payment-intent/`

Request
```json
{"plan_id": 2}
```

Response
```json
{"client_secret": "pi_3SK..._secret_xxx", "amount": 7900, "currency": "usd"}
```

### Affiliates

- GET `/api/affiliates/stats/` (Response)
```json
{
  "total_referrals": 3,
  "active_referrals": 2,
  "total_commission_earned": 150.0,
  "total_commission_paid": 100.0,
  "total_commission_pending": 50.0,
  "last_updated": "2025-10-20T09:00:00Z",
  "referral_link": "http://localhost:3000/register?ref=0E93C3E5"
}
```

- GET `/api/affiliates/commissions/?status=paid&page=1&page_size=20` (Response)
```json
{
  "commissions": [
    {"id": 7, "referred_user": {"id": 14, "username": "patient1", "email": "patient1@example.com", "first_name": "Pat", "last_name": "Ient", "user_type": "patient", "phone_number": null, "is_verified": false, "referral_code": "36C93C3D", "created_at": "2025-09-10T10:00:00Z", "profile": {...}}, "commission_amount": 41.1, "commission_percentage": 30.0, "commission_type": "subscription", "status": "paid", "paid_at": "2025-10-01T12:00:00Z", "created_at": "2025-09-01T12:00:00Z"}
  ],
  "total_count": 4,
  "page": 1,
  "page_size": 20,
  "has_next": false
}
```

- POST `/api/affiliates/generate-link/` (Response)
```json
{
  "message": "Affiliate link generated successfully",
  "affiliate_link": "http://localhost:3000/register?ref=0E93C3E5",
  "referral_code": "0E93C3E5"
}
```

- GET `/api/affiliates/dashboard/` (Response)
```json
{
  "total_earnings": 150.0,
  "available_balance": 50.0,
  "total_referrals": 3,
  "monthly_earnings": 41.1,
  "affiliate_link": "http://localhost:3000/register?ref=0E93C3E5",
  "referral_code": "0E93C3E5",
  "recent_commissions": [...],
  "recent_referrals": [...],
  "recent_payouts": []
}
```

- GET `/api/affiliates/payouts/` (Response)
```json
{"payout_requests": [{"id": 3, "amount": 50.0, "status": "pending", "payment_method": "paypal", "payment_details": {"paypal_email": "affiliate@example.com"}, "processed_at": null, "rejection_reason": null, "created_at": "2025-10-15T11:00:00Z"}]}
```

- POST `/api/affiliates/payouts/`

Request
```json
{"amount": 50.0, "payment_method": "paypal", "payment_details": {"paypal_email": "affiliate@example.com"}}
```

Response
```json
{"message": "Payout request created successfully", "payout_request": {"id": 4, "amount": 50.0, "status": "pending", "payment_method": "paypal", "payment_details": {"paypal_email": "affiliate@example.com"}, "processed_at": null, "rejection_reason": null, "created_at": "2025-10-22T01:00:00Z"}}
```

### Nutrition

- GET `/api/nutrition/diseases/` (Response)
```json
{"diseases": [{"id": 1, "name": "Diabetes Type 2", "description": "Requires reduced calorie intake and controlled carbohydrates", "dietary_restrictions": null, "calorie_adjustment": -200}]}
```

- POST `/api/nutrition/plans/`

Request
```json
{
  "name": "Weight Loss - 8 weeks",
  "age": 32,
  "gender": "male",
  "height": 178,
  "weight": 86,
  "activity_level": "moderate",
  "goal": "lose",
  "disease_ids": [1],
  "allergies": "Peanuts",
  "medications": "Metformin",
  "notes": "Check-in weekly"
}
```

Response
```json
{
  "message": "Nutrition plan created successfully",
  "nutrition_plan": {
    "id": 21,
    "name": "Weight Loss - 8 weeks",
    "age": 32,
    "gender": "male",
    "height": 178,
    "weight": 86,
    "activity_level": "moderate",
    "goal": "lose",
    "diseases": [{"id": 1, "name": "Diabetes Type 2", "description": "Requires reduced calorie intake and controlled carbohydrates", "dietary_restrictions": null, "calorie_adjustment": -200}],
    "allergies": "Peanuts",
    "medications": "Metformin",
    "bmr": 1780.45,
    "tdee": 2750.12,
    "target_calories": 2550.12,
    "protein_grams": 159.38,
    "carbs_grams": 286.26,
    "fat_grams": 85.00,
    "meal_plan": {},
    "notes": "Check-in weekly",
    "is_active": true,
    "created_at": "2025-10-22T00:30:00Z",
    "updated_at": "2025-10-22T00:30:00Z"
  }
}
```

- GET `/api/nutrition/plans/<plan_id>/` (Response)
```json
{"nutrition_plan": {"id": 21, "name": "Weight Loss - 8 weeks", "age": 32, "gender": "male", "height": 178, "weight": 86, "activity_level": "moderate", "goal": "lose", "diseases": [...], "allergies": "Peanuts", "medications": "Metformin", "bmr": 1780.45, "tdee": 2750.12, "target_calories": 2550.12, "protein_grams": 159.38, "carbs_grams": 286.26, "fat_grams": 85.0, "meal_plan": {}, "notes": "Check-in weekly", "is_active": true, "created_at": "2025-10-22T00:30:00Z", "updated_at": "2025-10-22T00:30:00Z"}}
```

- PUT `/api/nutrition/plans/<plan_id>/`

Request
```json
{"notes": "Increase daily steps to 8k"}
```

Response
```json
{"message": "Nutrition plan updated successfully", "nutrition_plan": {"id": 21, "notes": "Increase daily steps to 8k", "updated_at": "2025-10-22T01:10:00Z"}}
```

- POST `/api/nutrition/calculate/`

Request
```json
{
  "name": "Quick Calc",
  "age": 30,
  "gender": "female",
  "height": 165,
  "weight": 60,
  "activity_level": "light",
  "goal": "maintain",
  "disease_ids": []
}
```

Response
```json
{"bmr": 1400.12, "tdee": 1750.55, "target_calories": 1750.55, "protein_grams": 109.41, "carbs_grams": 196.73, "fat_grams": 58.35}
```

- POST `/api/nutrition/whatsapp/`

Request
```json
{"phone_number": "+15555550123", "message": "Remember your lunch at 1pm"}
```

Response
```json
{"message": "WhatsApp message sent successfully (demo)", "sent_message": {"id": 10, "phone_number": "+15555550123", "message_type": "outgoing", "content": "Remember your lunch at 1pm", "whatsapp_message_id": null, "status": "sent", "created_at": "2025-10-22T00:40:00Z"}}
```
