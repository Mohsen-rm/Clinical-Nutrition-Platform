# 🏥 Clinical Nutrition Platform - دليل المشروع الشامل

## نظرة عامة على المشروع

منصة إدارة التغذية السريرية هي نظام شامل لإدارة التغذية العلاجية مع نظام أدوار متقدم، نظام اشتراكات، ونظام عمولات للشركاء.

## 🎯 الهدف من المشروع

- **إدارة المرضى والأطباء**: نظام أدوار منفصل للأطباء والمرضى
- **نظام الاشتراكات**: دفع شهري عبر Stripe مع خطط متعددة
- **نظام الشراكة**: عمولة 30% متكررة على الإحالات
- **حسابات التغذية**: حسابات السعرات الحرارية حسب الحالة الصحية
- **تكامل WhatsApp**: إرسال نصائح تغذوية ومتابعة

## 🏗️ معمارية النظام

### Backend (Django)
```
backend/
├── clinical_platform/          # إعدادات Django الرئيسية
│   ├── settings.py            # إعدادات المشروع
│   ├── urls.py               # توجيه URLs الرئيسي
│   └── wsgi.py               # إعداد WSGI
├── apps/                     # تطبيقات Django
│   ├── accounts/             # إدارة المستخدمين والمصادقة
│   ├── subscriptions/        # نظام الاشتراكات وStripe
│   ├── affiliates/          # نظام الشراكة والعمولات
│   └── nutrition/           # حسابات التغذية وWhatsApp
├── requirements.txt         # مكتبات Python
├── manage.py               # أداة إدارة Django
└── .env                    # متغيرات البيئة
```

### Frontend (React)
```
frontend/
├── src/
│   ├── components/          # مكونات قابلة للإعادة
│   │   ├── ui/             # مكونات واجهة المستخدم
│   │   ├── Layout.jsx      # تخطيط الصفحة الرئيسي
│   │   └── ProtectedRoute.jsx # حماية الصفحات
│   ├── pages/              # صفحات التطبيق
│   │   ├── Home.jsx        # الصفحة الرئيسية
│   │   ├── Login.jsx       # صفحة تسجيل الدخول
│   │   ├── Register.jsx    # صفحة التسجيل
│   │   ├── Dashboard.jsx   # لوحة التحكم
│   │   ├── Subscription.jsx # إدارة الاشتراكات
│   │   ├── SubscriptionPlans.jsx # اختيار الخطط
│   │   ├── Checkout.jsx    # صفحة الدفع
│   │   ├── Affiliate.jsx   # لوحة الشراكة
│   │   ├── Profile.jsx     # الملف الشخصي
│   │   └── NutritionPlan.jsx # خطط التغذية
│   ├── lib/                # مكتبات مساعدة
│   │   ├── api.js          # عميل API
│   │   └── utils.js        # وظائف مساعدة
│   ├── store/              # إدارة الحالة
│   │   └── authStore.js    # حالة المصادقة
│   ├── App.js              # مكون التطبيق الرئيسي
│   └── index.js            # نقطة دخول التطبيق
├── package.json            # تبعيات Node.js
├── tailwind.config.js      # إعداد Tailwind CSS
└── .env                    # متغيرات البيئة
```

## 🔧 التقنيات المستخدمة

### Backend
- **Django 4.2.16**: إطار عمل الويب الرئيسي
- **Django REST Framework**: لبناء API
- **PostgreSQL**: قاعدة البيانات
- **Stripe**: معالجة المدفوعات
- **JWT**: المصادقة
- **Celery**: المهام غير المتزامنة
- **Redis**: تخزين مؤقت ووسيط رسائل

### Frontend
- **React 18**: مكتبة واجهة المستخدم
- **React Router**: التنقل
- **TanStack Query**: إدارة حالة الخادم
- **Zustand**: إدارة الحالة المحلية
- **Tailwind CSS**: تصميم واجهة المستخدم
- **Stripe.js**: تكامل المدفوعات
- **Axios**: عميل HTTP

## 🚀 طريقة التشغيل

### 1. إعداد Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # على macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python create_sample_data.py
python manage.py runserver
```

### 2. إعداد Frontend
```bash
cd frontend
npm install
npm start
```

### 3. إعداد قاعدة البيانات
```bash
# تثبيت PostgreSQL
brew install postgresql
brew services start postgresql

# إنشاء قاعدة البيانات
createdb clinical_nutrition_db
```

## 🔐 بيانات الاختبار

### حسابات المستخدمين
- **مدير النظام**: admin@example.com / admin123
- **طبيب**: doctor@example.com / doctor123  
- **مريض**: patient@example.com / patient123

### خطط الاشتراك
1. **Basic Plan** - $29/شهر
2. **Professional Plan** - $79/شهر
3. **Enterprise Plan** - $149/شهر

## 🔗 الربط بين Frontend و Backend

### 1. إعداد API Client
```javascript
// frontend/src/lib/api.js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### 2. المصادقة
```javascript
// تخزين الرموز المميزة
localStorage.setItem('access_token', tokens.access);
localStorage.setItem('refresh_token', tokens.refresh);

// إضافة الرمز المميز للطلبات
config.headers.Authorization = `Bearer ${token}`;
```

### 3. إدارة الحالة
```javascript
// frontend/src/store/authStore.js
const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      login: (userData, tokens) => { /* ... */ },
      logout: () => { /* ... */ },
    })
  )
);
```

## 📡 نقاط النهاية الرئيسية (API Endpoints)

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

## 🎨 نظام التصميم

### الألوان الرئيسية
```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96%;
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}
```

### المكونات الأساسية
- **Card**: بطاقات المحتوى
- **Button**: أزرار التفاعل
- **Input**: حقول الإدخال
- **Toast**: رسائل التنبيه

## 💳 تكامل Stripe

### إعداد المدفوعات المحدث
```javascript
// تحميل Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// إنشاء PaymentMethod مباشرة (التدفق المحسن)
const { error, paymentMethod } = await stripe.createPaymentMethod({
  type: 'card',
  card: cardElement,
});

// إنشاء الاشتراك مباشرة مع PaymentMethod
if (!error) {
  await subscriptionAPI.createSubscription({
    plan_id: plan.id,
    payment_method_id: paymentMethod.id,
  });
}
```

## 🤝 نظام الشراكة

### آلية العمل
1. **إنشاء رمز إحالة** لكل مستخدم
2. **تتبع التسجيلات** عبر الرمز
3. **حساب العمولة** 30% من قيمة الاشتراك
4. **دفع العمولات** عند الطلب (حد أدنى $50)

### تتبع العمولات
```python
# backend/apps/affiliates/models.py
class AffiliateCommission(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE)
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
```

## 🏥 منطق التغذية العلاجية

### حساب السعرات الحرارية
```python
# معادلة Harris-Benedict
if gender == 'male':
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
else:
    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

# إضافة مستوى النشاط
tdee = bmr * activity_multiplier

# تعديل حسب الأمراض
for disease in diseases:
    tdee += disease.calorie_adjustment
```

### الأمراض والتعديلات
- **السكري النوع 2**: -200 سعرة حرارية
- **فرط نشاط الغدة الدرقية**: +300 سعرة حرارية
- **ارتفاع ضغط الدم**: -100 سعرة حرارية

## 📱 تكامل WhatsApp

### إرسال الرسائل
```python
# backend/apps/nutrition/models.py
class WhatsAppMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=20)  # tip, reminder
    sent_at = models.DateTimeField(auto_now_add=True)
```

## 🔒 الأمان

### حماية API
- **JWT Tokens**: للمصادقة
- **CORS**: للحماية من الطلبات الخارجية
- **Rate Limiting**: لمنع الإساءة
- **Input Validation**: للتحقق من البيانات

### حماية Frontend
- **Protected Routes**: للصفحات المحمية
- **Token Refresh**: تجديد الرموز المميزة تلقائياً
- **Error Handling**: معالجة الأخطاء بشكل آمن

## 🚀 النشر والإنتاج

### متطلبات النشر
- **Backend**: Gunicorn + Nginx
- **Frontend**: Build static files
- **Database**: PostgreSQL production
- **Cache**: Redis
- **Storage**: AWS S3 للملفات

### متغيرات البيئة
```bash
# Backend
SECRET_KEY=production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
STRIPE_SECRET_KEY=sk_live_...

# Frontend  
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

## 📊 المراقبة والتحليلات

### مؤشرات الأداء
- **عدد المستخدمين النشطين**
- **معدل التحويل للاشتراكات**
- **إيرادات الشراكة**
- **استخدام ميزات التغذية**

## 🔄 التطوير المستقبلي

### الميزات المخططة
- **تطبيق موبايل**: React Native
- **تحليلات متقدمة**: Dashboard للإحصائيات
- **AI للتغذية**: توصيات ذكية
- **تكامل أوسع**: مع أنظمة المستشفيات

## 📞 الدعم والمساعدة

### الموارد
- **الكود المصدري**: GitHub Repository
- **التوثيق**: /docs folder
- **API Documentation**: Swagger/OpenAPI
- **اختبارات**: Unit & Integration tests

## 🆕 التحديثات الأخيرة

### إصلاحات نظام الاشتراكات
- **حل أخطاء Stripe**: إصلاح مشاكل "No such price" و "current_period_start"
- **تحسين تجربة المستخدم**: صفحات منفصلة لإدارة الاشتراك واختيار الخطط
- **تدفق دفع محسن**: استخدام `createPaymentMethod` مباشرة بدلاً من `PaymentIntent`
- **معالجة أخطاء شاملة**: سجلات تفصيلية ومعالجة آمنة للحقول المفقودة

### الميزات الجديدة
- **صفحة إدارة الاشتراك**: واجهة مخصصة للمشتركين النشطين
- **صفحة اختيار الخطط**: `/subscription/plans` لعرض جميع الخطط
- **التوجيه الذكي**: المشتركون يرون إدارة الاشتراك، الجدد يرون اختيار الخطط
- **مؤشرات الخطة الحالية**: تمييز واضح للخطة النشطة

### التحسينات التقنية
```python
# معالجة آمنة لحقول Stripe
if hasattr(subscription, 'current_period_start') and subscription.current_period_start:
    current_period_start = timezone.datetime.fromtimestamp(
        subscription.current_period_start, tz=timezone.utc
    )

# إضافة حقول جديدة للـ serializers
class SubscriptionSerializer(serializers.ModelSerializer):
    plan_id = serializers.ReadOnlyField(source='plan.id')
    plan_name = serializers.ReadOnlyField(source='plan.name')
    amount = serializers.SerializerMethodField()
```

### أسعار Stripe الجديدة
```
Basic Plan: price_1SKnPGKIRFVcVGUq7pDWmpzx ($29/month)
Professional Plan: price_1SKnPHKIRFVcVGUqPYQOa3Zl ($79/month)  
Enterprise Plan: price_1SKnPIKIRFVcVGUqHyLdIQkr ($149/month)
```

### الملفات المحدثة
- `frontend/src/pages/Subscription.jsx` - صفحة إدارة الاشتراك
- `frontend/src/pages/SubscriptionPlans.jsx` - صفحة اختيار الخطط (جديد)
- `backend/apps/subscriptions/stripe_service.py` - تحسين create_subscription
- `backend/apps/subscriptions/serializers.py` - إضافة حقول جديدة

---

**تم إنشاء هذا التوثيق في**: أكتوبر 2025  
**الإصدار**: 1.1.0  
**المطور**: Mohsen  
**الحالة**: مكتمل ومجهز للإنتاج مع تحسينات UX وإصلاحات Stripe
