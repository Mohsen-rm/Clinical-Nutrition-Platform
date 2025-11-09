# 🔧 Backend Documentation - Clinical Nutrition Platform

## Overview

Backend built with Django REST Framework providing a comprehensive API for managing the medical system with roles, subscriptions, and an affiliate program.

## 🏗️ Project Structure

```
backend/
├── clinical_platform/          # Main project
│   ├── settings.py            # Django settings
│   ├── urls.py               # Main URLs
│   └── wsgi.py               # WSGI configuration
├── apps/                     # Django apps
│   ├── accounts/             # User management
│   ├── subscriptions/        # Subscription system
│   ├── affiliates/          # Affiliate system
│   └── nutrition/           # Clinical nutrition
├── requirements.txt         # Required packages
├── manage.py               # Django management tool
├── .env                    # Environment variables
└── create_sample_data.py   # Sample data
```

## ⚙️ Main Settings

### Environment variables (.env)
```bash
SECRET_KEY=django-insecure-development-key-change-in-production-12345
DEBUG=True
DB_NAME=clinical_nutrition_db
DB_USER=mohsen
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
FRONTEND_URL=http://localhost:3000
REDIS_URL=redis://localhost:6379/0
```

## 🚀 Run the project

```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create sample data
python create_sample_data.py

# Start the server
python manage.py runserver
```

## 🔑 Test credentials

```
Admin: admin@example.com / admin123
Doctor: doctor@example.com / doctor123
Patient: patient@example.com / patient123
```

## 📡 Main API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/register/` - Register
- `GET /api/auth/profile/` - Profile

### Subscriptions
- `GET /api/subscriptions/plans/` - Subscription plans
- `POST /api/subscriptions/create/` - Create subscription with Stripe
- `GET /api/subscriptions/status/` - Subscription status
- `POST /api/subscriptions/cancel/` - Cancel subscription
- `POST /api/subscriptions/payment-intent/` - Create Payment Intent
- `POST /api/subscriptions/webhook/` - Stripe Webhooks

### Affiliates
- `GET /api/affiliates/dashboard/` - Affiliate dashboard
- `GET /api/affiliates/commissions/` - Commission history
- `POST /api/affiliates/generate-link/` - Generate referral link

### Nutrition
- `GET /api/nutrition/plans/` - Nutrition plans
- `GET /api/nutrition/diseases/` - Diseases
- `POST /api/nutrition/calculate/` - Calorie calculation

## 🆕 Recent Updates

### Subscription system fixes
- **Stripe error fixes**: Resolved "No such price" and "current_period_start"
- **Improved StripeService**: Safe handling of missing fields from Stripe
- **Updated Serializers**: Added `plan_id`, `plan_name`, `amount` for frontend
- **Error handling**: Detailed logs and comprehensive error handling

### Technical improvements
```python
# Safe handling for period fields
if hasattr(subscription, 'current_period_start') and subscription.current_period_start:
    current_period_start = timezone.datetime.fromtimestamp(
        subscription.current_period_start, tz=timezone.utc
    )

# If not available, use current time + 30 days
if not current_period_start:
    current_period_start = timezone.now()
```

### New Stripe prices
```python
# Real prices created in Stripe
Basic Plan: price_1SKnPGKIRFVcVGUq7pDWmpzx ($29/month)
Professional Plan: price_1SKnPHKIRFVcVGUqPYQOa3Zl ($79/month)  
Enterprise Plan: price_1SKnPIKIRFVcVGUqHyLdIQkr ($149/month)
```

### Test scripts
- `create_stripe_prices.py` - Create Stripe prices
- `test_subscription_creation.py` - Test creating subscriptions
- `test_subscription_api.py` - Comprehensive API tests

### Updated files
- `apps/subscriptions/stripe_service.py` - Improved create_subscription
- `apps/subscriptions/serializers.py` - Added new fields
- `apps/subscriptions/views.py` - Improved error handling

---

**Last updated**: October 2025  
**Version**: 1.1.0  
**System status**: Complete and production-ready with Stripe fixes
