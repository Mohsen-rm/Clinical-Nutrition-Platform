# Clinical Nutrition Platform

A comprehensive SaaS platform for clinical nutrition management with subscription-based access, role-based authentication, and affiliate system.

## Features

### Core Features
- **Two User Roles**: Doctor (professional) and Patient (regular)
- **Authentication**: JWT tokens with secure token refresh
- **Stripe Integration**: Complete subscription system with multiple plans ($29-$149/month)
- **Subscription Management**: Dedicated pages for subscription management and plan selection
- **Affiliate System**: 30% recurring commission for referrals with tracking
- **Nutrition Calculator**: Disease-specific calorie adjustments and meal planning
- **Admin Panel**: User and revenue analytics management
- **Modern UI**: React with responsive design and professional components
- **WhatsApp Integration**: Communication and nutrition tips delivery

### Technical Stack
- **Backend**: Django 4.2+ with Django REST Framework
- **Frontend**: React 18+ with modern UI components
- **Database**: PostgreSQL
- **Payment**: Stripe API
- **Authentication**: JWT + Django sessions
- **Styling**: TailwindCSS + shadcn/ui components

## Project Structure

```
clinical_nutrition_platform/
├── backend/                 # Django backend
│   ├── clinical_platform/   # Main Django project
│   ├── apps/               # Django applications
│   │   ├── accounts/       # User management & auth
│   │   ├── subscriptions/  # Stripe integration
│   │   ├── affiliates/     # Affiliate system
│   │   └── nutrition/      # Nutrition logic
│   ├── requirements.txt    # Python dependencies
│   └── manage.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom hooks
│   │   └── utils/         # Utilities
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Stripe account (for payments)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create `.env` files in both backend and frontend directories with the required configuration (see `.env.example` files).

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile

### Subscriptions
- `GET /api/subscriptions/plans/` - Get subscription plans
- `POST /api/subscriptions/create/` - Create subscription with Stripe
- `GET /api/subscriptions/status/` - Check subscription status
- `POST /api/subscriptions/cancel/` - Cancel subscription
- `POST /api/subscriptions/payment-intent/` - Create payment intent

### Affiliates
- `GET /api/affiliates/dashboard/` - Get affiliate dashboard data
- `GET /api/affiliates/commissions/` - Get commission history
- `POST /api/affiliates/generate-link/` - Generate referral link

### Nutrition
- `GET /api/nutrition/plans/` - Get nutrition plans
- `POST /api/nutrition/calculate/` - Calculate nutrition requirements

## Development

### Running Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Database Migration
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## Recent Updates

### Subscription System Improvements
- **Fixed Stripe Integration**: Resolved "No such price" and "current_period_start" errors
- **Enhanced User Experience**: Separate pages for subscription management and plan selection
- **Smart Routing**: Active subscribers see management dashboard, new users see plan selection
- **Comprehensive Error Handling**: Robust error handling for all Stripe operations

### Key Features Added
- **Subscription Management Page**: Dedicated interface for active subscribers
- **Plan Selection Page**: Clean interface for choosing/changing plans
- **Payment Flow**: Streamlined checkout process with Stripe Elements
- **Affiliate Tracking**: Complete referral system with commission tracking
- **Responsive Design**: Mobile-friendly interface across all pages

### Technical Improvements
- **JWT Token Management**: Secure token refresh mechanism
- **API Optimization**: Enhanced serializers with required frontend data
- **Error Logging**: Comprehensive debugging and error tracking
- **Database Optimization**: Efficient queries and data relationships

## Deployment

The application is configured for deployment on platforms like Heroku, DigitalOcean, or AWS.

### Environment Configuration
```bash
# Backend (.env)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
DATABASE_URL=postgresql://...

# Frontend (.env)
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
REACT_APP_API_URL=http://localhost:8000
```

## Testing

### Test Credentials
- **Admin**: admin@example.com / admin123
- **Doctor**: doctor@example.com / doctor123
- **Patient**: patient@example.com / patient123

### Stripe Test Cards
- **Success**: 4242424242424242
- **Decline**: 4000000000000002

## License

This project is for evaluation purposes as part of a technical test.
# Clinical-Nutrition-Platform
