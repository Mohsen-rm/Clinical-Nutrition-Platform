# 💰 دليل نظام العمولات 30% - Clinical Nutrition Platform

## نظرة عامة

نظام العمولات يوفر **30% عمولة متكررة** للشركاء على كل اشتراك يتم من خلال رابط الإحالة الخاص بهم.

## 🔄 طرق تفعيل نظام العمولات

### 1. المعالجة التلقائية (موصى بها)

#### أ) تشغيل السكريبت التلقائي
```bash
cd backend
python process_affiliate_commissions.py
```

**الميزات:**
- معالجة جميع المدفوعات الجديدة تلقائياً
- حساب العمولة 30% لكل مدفوعة
- تحديث إحصائيات الشركاء
- إنشاء تقارير مفصلة

#### ب) استخدام Celery للمعالجة المجدولة
```bash
# تشغيل Celery Worker
celery -A clinical_platform worker -l info

# تشغيل Celery Beat للمهام المجدولة
celery -A clinical_platform beat -l info
```

**الجدولة التلقائية:**
- **يومياً 2:00 ص**: معالجة العمولات الجديدة
- **يومياً 3:00 ص**: تحديث إحصائيات الشركاء
- **أسبوعياً (الاثنين 9:00 ص)**: إرسال إشعارات للشركاء
- **شهرياً (أول الشهر 1:00 ص)**: تنظيف العمولات القديمة

### 2. المعالجة اليدوية

#### تشغيل المدير اليدوي
```bash
cd backend
python manual_commission_manager.py
```

**الميزات المتاحة:**
1. **📊 عرض تقرير العمولات** - إحصائيات شاملة
2. **👥 عرض الشركاء وإحصائياتهم** - قائمة جميع الشركاء
3. **💰 عرض العمولات المعلقة** - العمولات غير المدفوعة
4. **✅ تحديد عمولات كمدفوعة** - تحديث حالة العمولات
5. **🔍 البحث عن شريك معين** - تفاصيل شريك محدد
6. **📋 عرض طلبات السحب** - طلبات سحب العمولات
7. **➕ إنشاء عمولة يدوياً** - إضافة عمولة خاصة
8. **🔄 تحديث إحصائيات الشركاء** - تحديث جميع الإحصائيات
9. **📈 تقرير مفصل لشريك** - تقرير شامل لشريك واحد

## 📊 كيفية عمل النظام

### 1. تتبع الإحالات
```python
# عند التسجيل برابط إحالة
user.referred_by = affiliate_user
user.save()
```

### 2. حساب العمولة
```python
# عند نجاح الدفع
commission_amount = payment.amount * 0.30  # 30%
```

### 3. إنشاء سجل العمولة
```python
AffiliateCommission.objects.create(
    affiliate=affiliate,
    referred_user=referred_user,
    payment=payment,
    commission_amount=commission_amount,
    commission_percentage=30.00,
    status='pending'
)
```

## 🛠️ الأوامر المتاحة

### السكريبت التلقائي
```bash
# معالجة العمولات
python process_affiliate_commissions.py

# عرض تقرير فقط
python process_affiliate_commissions.py report

# تحديد عمولات كمدفوعة
python process_affiliate_commissions.py pay

# تحديد عمولات شريك معين كمدفوعة
python process_affiliate_commissions.py pay admin@example.com
```

### المدير اليدوي
```bash
# تشغيل المدير التفاعلي
python manual_commission_manager.py
```

### مهام Celery
```python
# تشغيل معالجة العمولات يدوياً
from apps.affiliates.tasks import process_affiliate_commissions
result = process_affiliate_commissions.delay()

# تحديث الإحصائيات
from apps.affiliates.tasks import update_affiliate_stats
result = update_affiliate_stats.delay()
```

## 📈 مراقبة النظام

### 1. فحص العمولات المعلقة
```bash
python manage.py shell -c "
from apps.affiliates.models import AffiliateCommission
pending = AffiliateCommission.objects.filter(status='pending')
print(f'العمولات المعلقة: {pending.count()}')
print(f'إجمالي المبلغ: ${sum(c.commission_amount for c in pending)}')
"
```

### 2. فحص إحصائيات الشركاء
```bash
python manage.py shell -c "
from apps.affiliates.models import AffiliateStats
stats = AffiliateStats.objects.all()
for stat in stats:
    print(f'{stat.user.email}: ${stat.total_commission_earned} ({stat.total_referrals} إحالات)')
"
```

### 3. فحص المدفوعات الجديدة
```bash
python manage.py shell -c "
from apps.subscriptions.models import Payment
new_payments = Payment.objects.filter(
    status='succeeded',
    affiliate_commission__isnull=True,
    subscription__user__referred_by__isnull=False
)
print(f'مدفوعات جديدة تحتاج معالجة: {new_payments.count()}')
"
```

## 🔧 إعداد النظام

### 1. إضافة إعدادات Celery
```python
# في settings.py
from celery_schedule import CELERY_BEAT_SCHEDULE

CELERY_BEAT_SCHEDULE = CELERY_BEAT_SCHEDULE
CELERY_TIMEZONE = 'UTC'
```

### 2. إعداد Redis (للـ Celery)
```bash
# تثبيت Redis
brew install redis  # على macOS
sudo apt install redis-server  # على Ubuntu

# تشغيل Redis
redis-server
```

### 3. تثبيت مكتبات إضافية
```bash
pip install celery redis django-celery-beat
```

## 📋 تقارير العمولات

### تقرير يومي
```bash
python process_affiliate_commissions.py report
```

### تقرير شريك معين
```bash
python manual_commission_manager.py
# اختر الخيار 9: تقرير مفصل لشريك
```

### تقرير العمولات المعلقة
```bash
python manual_commission_manager.py
# اختر الخيار 3: عرض العمولات المعلقة
```

## 💳 معالجة المدفوعات

### تحديد جميع العمولات كمدفوعة
```bash
python manual_commission_manager.py
# اختر الخيار 4 ثم 1: تحديد جميع العمولات المعلقة
```

### تحديد عمولات شريك معين
```bash
python manual_commission_manager.py
# اختر الخيار 4 ثم 2: تحديد عمولات شريك معين
```

### تحديد عمولات محددة
```bash
python manual_commission_manager.py
# اختر الخيار 4 ثم 3: تحديد عمولات محددة بالـ ID
```

## 🚨 استكشاف الأخطاء

### مشكلة: العمولات لا تُحسب
```bash
# فحص المدفوعات
python manage.py shell -c "
from apps.subscriptions.models import Payment
payments = Payment.objects.filter(status='succeeded')
print(f'إجمالي المدفوعات الناجحة: {payments.count()}')
"

# فحص الإحالات
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
referred_users = User.objects.filter(referred_by__isnull=False)
print(f'المستخدمون المُحالون: {referred_users.count()}')
"
```

### مشكلة: Celery لا يعمل
```bash
# فحص حالة Celery
celery -A clinical_platform inspect active

# فحص المهام المجدولة
celery -A clinical_platform inspect scheduled
```

### مشكلة: الإحصائيات غير صحيحة
```bash
# تحديث جميع الإحصائيات
python manual_commission_manager.py
# اختر الخيار 8: تحديث إحصائيات الشركاء
```

## 📞 الدعم

### سجلات النظام
```bash
# عرض سجلات Django
tail -f logs/django.log

# عرض سجلات Celery
tail -f logs/celery.log
```

### اختبار النظام
```bash
# إنشاء بيانات تجريبية
python create_sample_data.py

# اختبار معالجة العمولات
python process_affiliate_commissions.py
```

---

**📅 آخر تحديث**: أكتوبر 2025  
**🔧 الإصدار**: 1.0.0  
**✅ الحالة**: جاهز للإنتاج
