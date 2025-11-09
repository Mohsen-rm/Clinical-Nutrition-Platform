# 🔧 Backend Documentation - Clinical Nutrition Platform

## Overview

Backend built with Django REST Framework providing a comprehensive API for managing the medical system with roles, subscriptions, and an affiliate program.

## 🏗️ Project Structure

```
backend/
├── clinical_platform/          # Main project
│   ├── __init__.py
│   ├── settings.py            # Django settings
│   ├── urls.py               # Main URLs
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
├── apps/                     # Django apps
│   ├── accounts/             # User management
│   ├── subscriptions/        # Subscription system
│   ├── affiliates/          # Affiliate system
│   └── nutrition/           # Clinical nutrition
├── logs/                    # Log files
├── static/                  # Static files
├── media/                   # User-uploaded files
├── requirements.txt         # Required packages
├── manage.py               # Django management tool
├── .env                    # Environment variables
└── create_sample_data.py   # Sample data
```

## ⚙️ Main Settings

### settings.py
```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='clinical_nutrition_db'),
        'USER': config('DB_USER', default='mohsen'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'apps.accounts',
    'apps.subscriptions',
    'apps.affiliates',
    'apps.nutrition',
]

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### Environment variables (.env)
```bash
SECRET_KEY=django-insecure-development-key-change-in-production-12345
DEBUG=True
DB_NAME=clinical_nutrition_db
DB_USER=mohsen
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
FRONTEND_URL=http://localhost:3000
REDIS_URL=redis://localhost:6379/0
```

## 👥 Accounts App

### Models
```python
# apps/accounts/models.py
class User(AbstractUser):
    USER_TYPES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patient')
    is_verified = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    address = models.TextField(blank=True)
```

### Views
```python
# apps/accounts/views.py
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
```

### URLs
```python
# apps/accounts/urls.py
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('referral/<str:code>/', CheckReferralCodeView.as_view(), name='check_referral'),
]
```

## 💳 Subscriptions App

### Models
```python
# apps/subscriptions/models.py
class SubscriptionPlan(models.Model):
    PLAN_TYPES = (
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('professional', 'Professional'),
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    stripe_price_id = models.CharField(max_length=100)
    features = models.JSONField(default=list)

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
```

### Stripe integration
```python
# apps/subscriptions/stripe_utils.py
import stripe

def create_stripe_customer(user):
    customer = stripe.Customer.create(
        email=user.email,
        name=f"{user.first_name} {user.last_name}",
        metadata={'user_id': user.id}
    )
    return customer

def create_subscription(customer_id, price_id):
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{'price': price_id}],
        payment_behavior='default_incomplete',
        expand=['latest_invoice.payment_intent'],
    )
    return subscription
```

### Webhooks
```python
# apps/subscriptions/webhooks.py
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    
    if event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_cancelled(event['data']['object'])
    
    return HttpResponse(status=200)
```

## 🤝 Affiliates App

### النماذج
```python
# apps/affiliates/models.py
class AffiliateStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_referrals = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class AffiliateCommission(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey('subscriptions.Subscription', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class PayoutRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
```

### Commission calculation
```python
# apps/affiliates/utils.py
def calculate_commission(subscription):
    """Calculate 30% commission from the subscription value"""
    commission_rate = Decimal('0.30')
    commission_amount = subscription.plan.price * commission_rate
    
    if subscription.user.referred_by:
        AffiliateCommission.objects.create(
            referrer=subscription.user.referred_by,
            referred_user=subscription.user,
            subscription=subscription,
            amount=commission_amount,
            status='pending'
        )
        
        # Update affiliate stats
        stats, created = AffiliateStats.objects.get_or_create(
            user=subscription.user.referred_by
        )
        stats.total_earnings += commission_amount
        stats.available_balance += commission_amount
        stats.save()
```

## 🏥 Nutrition App

### Models
```python
# apps/nutrition/models.py
class Disease(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    dietary_restrictions = models.TextField()
    calorie_adjustment = models.IntegerField(default=0)  # Calorie adjustment

class NutritionPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)
    age = models.IntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    gender = models.CharField(max_length=10)
    activity_level = models.CharField(max_length=20)
    goal = models.CharField(max_length=20)
    diseases = models.ManyToManyField(Disease, blank=True)
    calculated_calories = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WhatsAppMessage(models.Model):
    MESSAGE_TYPES = (
        ('tip', 'Nutrition Tip'),
        ('reminder', 'Reminder'),
        ('follow_up', 'Follow Up'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    sent_at = models.DateTimeField(auto_now_add=True)
```

### Calorie calculations
```python
# apps/nutrition/calculations.py
def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate using the Harris-Benedict equation"""
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return round(bmr)

def calculate_tdee(bmr, activity_level):
    """Calculate Total Daily Energy Expenditure"""
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return round(bmr * activity_multipliers.get(activity_level, 1.55))

def adjust_for_goal(tdee, goal):
    """Adjust calories based on goal"""
    if goal == 'lose':
        return tdee - 500  # Subtract 500 calories to lose ~0.5 kg/week
    elif goal == 'gain':
        return tdee + 500  # Add 500 calories to gain ~0.5 kg/week
    return tdee  # Maintain weight

def apply_disease_adjustments(calories, diseases):
    """Apply disease adjustments"""
    total_adjustment = 0
    adjustments = []
    
    for disease in diseases:
        total_adjustment += disease.calorie_adjustment
        adjustments.append({
            'disease': disease.name,
            'adjustment': disease.calorie_adjustment
        })
    
    return calories + total_adjustment, adjustments
```

## 🔧 Management commands

### Create sample data
```python
# create_sample_data.py
def create_sample_data():
    # Create subscription plans
    plans_data = [
        {
            'name': 'Basic Plan',
            'price': 29.00,
            'plan_type': 'basic',
            'features': ['Basic nutrition planning', 'Up to 50 patients']
        },
        # ...
    ]
    
    # Create diseases
    diseases_data = [
        {
            'name': 'Diabetes Type 2',
            'calorie_adjustment': -200,
            'dietary_restrictions': 'Low carbohydrate, controlled portions'
        },
        # ...
    ]
    
    # Create users
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
```

### Run tasks
```bash
# Apply database changes
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run the server
python manage.py runserver

# Create sample data
python create_sample_data.py
```

## 🔒 Security and permissions

### Custom permissions
```python
# apps/accounts/permissions.py
class IsDoctorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.user_type == 'doctor'

class IsOwnerOrDoctor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'doctor':
            return True
        return obj.user == request.user
```

### API protection
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

## 📊 Logging and monitoring

### Logging setup
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚀 Deployment

### Production settings
```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Production Database
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# إعدادات الأمان
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Production requirements
```txt
# requirements/production.txt
-r base.txt
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.8.2
sentry-sdk==1.32.0
```

## 🧪 Tests

### Unit tests
```python
# apps/accounts/tests.py
class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='doctor'
        )
        self.assertEqual(user.user_type, 'doctor')
        self.assertFalse(user.is_verified)

# Run tests
python manage.py test
```

## 📡 API Documentation

### Main endpoints

#### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/profile/` - Get profile
- `PUT /api/auth/profile/` - Update profile

#### Subscriptions
- `GET /api/subscriptions/plans/` - List subscription plans
- `POST /api/subscriptions/create/` - Create a new subscription
- `GET /api/subscriptions/status/` - Current subscription status
- `POST /api/subscriptions/cancel/` - Cancel subscription

#### Affiliates
- `GET /api/affiliates/stats/` - Affiliate statistics
- `GET /api/affiliates/commissions/` - List commissions
- `POST /api/affiliates/payouts/` - Request payout

#### Nutrition
- `GET /api/nutrition/diseases/` - List diseases
- `POST /api/nutrition/calculate/` - Calculate calories
- `GET /api/nutrition/plans/` - Nutrition plans
- `POST /api/nutrition/plans/` - Create a nutrition plan

---

**Last updated**: October 2025  
**Version**: 1.0.0  
**Code status**: Complete and production-ready
