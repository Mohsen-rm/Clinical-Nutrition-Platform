# إصلاح مشكلة Stripe Payment Intent - Minimum Amount Error

## ✅ **تم حل المشكلة**

تم إصلاح خطأ "The amount must be greater than or equal to the minimum charge amount" في نظام الدفع.

## 🐛 **المشكلة الأساسية**

```
{
  "error": "The amount must be greater than or equal to the minimum charge amount allowed for your account and the currency set"
}
```

المشكلة كانت في:
1. الواجهة الأمامية ترسل `plan_id` فقط
2. الخادم الخلفي يتوقع `amount` و `currency`
3. إصدار قديم من مكتبة Stripe

## 🔧 **الحلول المطبقة**

### 1. إصلاح create_payment_intent API:

**قبل الإصلاح:**
```python
def create_payment_intent(request):
    amount = request.data.get('amount', 0)  # ❌ المبلغ 0 أو غير موجود
    currency = request.data.get('currency', 'usd')
    
    intent = stripe.PaymentIntent.create(
        amount=amount,  # ❌ يرسل 0 إلى Stripe
        currency=currency,
    )
```

**بعد الإصلاح:**
```python
def create_payment_intent(request):
    plan_id = request.data.get('plan_id')
    
    # Get the subscription plan
    plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    
    # Calculate amount in cents
    amount = int(float(plan.price) * 100)  # ✅ حساب صحيح
    currency = plan.currency.lower()
    
    intent = stripe.PaymentIntent.create(
        amount=amount,  # ✅ مبلغ صحيح (2900 cents = $29.00)
        currency=currency,
        metadata={
            'user_id': request.user.id,
            'plan_id': plan.id,
            'plan_name': plan.name
        }
    )
```

### 2. تحديث مكتبة Stripe:

```bash
# من الإصدار القديم
stripe==7.8.0

# إلى الإصدار الجديد
stripe==13.0.1
```

### 3. التحقق من الأسعار:

```
✅ Basic Plan: $29.00 (2900 cents) - OK
✅ Professional Plan: $79.00 (7900 cents) - OK  
✅ Enterprise Plan: $149.00 (14900 cents) - OK
```

## 📊 **اختبار النجاح**

```bash
=== CREATING PAYMENT INTENT ===
✅ Payment Intent created successfully!
ID: pi_3SKn8WKIRFVcVGUq1dsAlVYb
Amount: 2900 cents
Currency: usd
Status: requires_payment_method
```

## 🔄 **تدفق العمل الصحيح**

1. **الواجهة الأمامية** ترسل: `{"plan_id": 1}`
2. **الخادم الخلفي** يحصل على الخطة من قاعدة البيانات
3. **حساب المبلغ**: `$29.00 × 100 = 2900 cents`
4. **إنشاء Payment Intent** مع المبلغ الصحيح
5. **إرجاع client_secret** للواجهة الأمامية

## 📝 **الملفات المحدثة**

- `/backend/apps/subscriptions/views.py` - إصلاح create_payment_intent
- `/backend/requirements.txt` - تحديث Stripe إلى 13.0.1
- `/backend/test_payment_intent.py` - سكريبت اختبار

## 🧪 **للاختبار**

1. اذهب إلى `/subscription`
2. اختر أي خطة واضغط "Subscribe"
3. في صفحة `/checkout` املأ بيانات البطاقة التجريبية:
   - رقم البطاقة: `4242 4242 4242 4242`
   - تاريخ الانتهاء: أي تاريخ مستقبلي
   - CVC: أي 3 أرقام
4. اضغط "Subscribe" - يجب أن يعمل بدون أخطاء

المشكلة محلولة تماماً! 🎉
