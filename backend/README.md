# 🔧 Backend Documentation - Clinical Nutrition Platform

## نظرة عامة

Backend مبني باستخدام Django REST Framework ويوفر API شامل لإدارة النظام الطبي مع نظام أدوار، اشتراكات، وشراكة.

## 🏗️ هيكل المشروع

```
backend/
├── clinical_platform/          # المشروع الرئيسي
│   ├── settings.py            # إعدادات Django
│   ├── urls.py               # URLs الرئيسية
│   └── wsgi.py               # WSGI configuration
├── apps/                     # تطبيقات Django
│   ├── accounts/             # إدارة المستخدمين
│   ├── subscriptions/        # نظام الاشتراكات
│   ├── affiliates/          # نظام الشراكة
│   └── nutrition/           # التغذية العلاجية
├── requirements.txt         # المكتبات المطلوبة
├── manage.py               # أداة إدارة Django
├── .env                    # متغيرات البيئة
└── create_sample_data.py   # بيانات تجريبية
```

## ⚙️ الإعدادات الرئيسية

### متغيرات البيئة (.env)
```bash
SECRET_KEY=django-insecure-development-key-change-in-production-12345
DEBUG=True
DB_NAME=clinical_nutrition_db
DB_USER=mohsen
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
STRIPE_PUBLISHABLE_KEY=pk_test_51SKkAIKIRFVcVGUq8YWP2sFe6Ag05MMcTo27DIAUqmnJEtXTYuTt0v2uoReyHLEke7UsHLIFvQrckVyMM6i0D4b000jdAIvthN
STRIPE_SECRET_KEY=sk_test_51SKkAIKIRFVcVGUq5AaM8F0oX8479wfG1EsXbMTU8Pm3WhGiDtbMX4vbjr2jViBXgMQDKtOstsWge3g5j9NS33np00AHEy2VGK
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
FRONTEND_URL=http://localhost:3000
REDIS_URL=redis://localhost:6379/0
```

## 🚀 تشغيل المشروع

```bash
# تفعيل البيئة الافتراضية
cd backend
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt

# تطبيق التغييرات على قاعدة البيانات
python manage.py migrate

# إنشاء البيانات التجريبية
python create_sample_data.py

# تشغيل الخادم
python manage.py runserver
```

## 🔑 بيانات الاختبار

```
Admin: admin@example.com / admin123
Doctor: doctor@example.com / doctor123
Patient: patient@example.com / patient123
```

## 📡 API Endpoints الرئيسية

### المصادقة
- `POST /api/auth/login/` - تسجيل الدخول
- `POST /api/auth/register/` - التسجيل
- `GET /api/auth/profile/` - الملف الشخصي

### الاشتراكات
- `GET /api/subscriptions/plans/` - خطط الاشتراك
- `POST /api/subscriptions/create/` - إنشاء اشتراك مع Stripe
- `GET /api/subscriptions/status/` - حالة الاشتراك
- `POST /api/subscriptions/cancel/` - إلغاء الاشتراك
- `POST /api/subscriptions/payment-intent/` - إنشاء Payment Intent
- `POST /api/subscriptions/webhook/` - Stripe Webhooks

### الشراكة
- `GET /api/affiliates/dashboard/` - لوحة تحكم الشراكة
- `GET /api/affiliates/commissions/` - تاريخ العمولات
- `POST /api/affiliates/generate-link/` - إنشاء رابط إحالة

### التغذية
- `GET /api/nutrition/plans/` - خطط التغذية
- `GET /api/nutrition/diseases/` - الأمراض
- `POST /api/nutrition/calculate/` - حساب السعرات

## 🆕 التحديثات الأخيرة

### إصلاحات نظام الاشتراكات
- **إصلاح أخطاء Stripe**: حل مشاكل "No such price" و "current_period_start"
- **تحسين StripeService**: معالجة آمنة للحقول المفقودة من Stripe
- **تحديث Serializers**: إضافة `plan_id`, `plan_name`, `amount` للواجهة الأمامية
- **معالجة الأخطاء**: سجلات تفصيلية وmعالجة شاملة للأخطاء

### تحسينات تقنية
```python
# معالجة آمنة لحقول الفترة
if hasattr(subscription, 'current_period_start') and subscription.current_period_start:
    current_period_start = timezone.datetime.fromtimestamp(
        subscription.current_period_start, tz=timezone.utc
    )

# إذا لم تكن متوفرة، استخدم الوقت الحالي + 30 يوم
if not current_period_start:
    current_period_start = timezone.now()
```

### أسعار Stripe الجديدة
```python
# تم إنشاء أسعار حقيقية في Stripe
Basic Plan: price_1SKnPGKIRFVcVGUq7pDWmpzx ($29/month)
Professional Plan: price_1SKnPHKIRFVcVGUqPYQOa3Zl ($79/month)  
Enterprise Plan: price_1SKnPIKIRFVcVGUqHyLdIQkr ($149/month)
```

### سكريبتات الاختبار
- `create_stripe_prices.py` - إنشاء أسعار Stripe
- `test_subscription_creation.py` - اختبار إنشاء الاشتراكات
- `test_subscription_api.py` - اختبار شامل لـ API

### الملفات المحدثة
- `apps/subscriptions/stripe_service.py` - تحسين create_subscription
- `apps/subscriptions/serializers.py` - إضافة حقول جديدة
- `apps/subscriptions/views.py` - تحسين معالجة الأخطاء

---

**آخر تحديث**: أكتوبر 2025  
**الإصدار**: 1.1.0  
**حالة النظام**: مكتمل ومجهز للإنتاج مع إصلاحات Stripe
