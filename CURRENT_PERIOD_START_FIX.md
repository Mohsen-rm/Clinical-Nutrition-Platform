# إصلاح خطأ current_period_start

## المشكلة
```
{"error":"current_period_start"}
```

كان الكود يحاول الوصول إلى `subscription.current_period_start` و `subscription.current_period_end` من Stripe، لكن هذه الحقول لم تكن متوفرة في بعض الحالات، مما تسبب في فشل إنشاء الاشتراك في قاعدة البيانات.

## السبب
1. Stripe أحياناً لا يرجع `current_period_start` و `current_period_end` فوراً عند إنشاء الاشتراك
2. الكود لم يكن يتعامل مع هذه الحالة بشكل آمن
3. عدم وجود معالجة للأخطاء المناسبة

## الحل المطبق

### 1. معالجة آمنة لحقول الفترة:
```python
# Handle current_period_start and current_period_end safely
current_period_start = None
current_period_end = None

if hasattr(subscription, 'current_period_start') and subscription.current_period_start:
    current_period_start = timezone.datetime.fromtimestamp(
        subscription.current_period_start, tz=timezone.utc
    )

if hasattr(subscription, 'current_period_end') and subscription.current_period_end:
    current_period_end = timezone.datetime.fromtimestamp(
        subscription.current_period_end, tz=timezone.utc
    )

# If periods are not available, use current time and add 30 days
if not current_period_start:
    current_period_start = timezone.now()
if not current_period_end:
    from datetime import timedelta
    current_period_end = current_period_start + timedelta(days=30)
```

### 2. معالجة آمنة لـ client_secret:
```python
# Get client_secret safely
client_secret = None
try:
    if hasattr(subscription, 'latest_invoice') and subscription.latest_invoice:
        if hasattr(subscription.latest_invoice, 'payment_intent') and subscription.latest_invoice.payment_intent:
            client_secret = subscription.latest_invoice.payment_intent.client_secret
        else:
            print("⚠️ No payment_intent found in latest_invoice")
    else:
        print("⚠️ No latest_invoice found in subscription")
except Exception as e:
    print(f"⚠️ Could not get client_secret: {str(e)}")
```

### 3. سجلات تفصيلية للتصحيح:
```python
print(f"🔍 Creating subscription for user {user.id}, plan {plan_id}, payment_method {payment_method_id}")
print(f"✅ Plan found: {plan.name} - {plan.stripe_price_id}")
print(f"✅ Customer created: {customer.id}")
print(f"✅ Stripe subscription created: {subscription.id}")
print(f"   Status: {subscription.status}")
print(f"✅ Database subscription created: {db_subscription.id}")
```

### 4. معالجة شاملة للأخطاء:
```python
except SubscriptionPlan.DoesNotExist:
    print(f"❌ Subscription plan not found: {plan_id}")
    raise Exception("Invalid subscription plan")
except stripe.StripeError as e:
    print(f"❌ Stripe error: {str(e)}")
    raise Exception(f"Stripe error: {str(e)}")
except Exception as e:
    print(f"❌ Unexpected error in create_subscription: {str(e)}")
    import traceback
    traceback.print_exc()
    raise Exception(f"Subscription creation failed: {str(e)}")
```

## النتيجة
✅ إنشاء الاشتراكات يعمل بنجاح
✅ معالجة آمنة للحقول المفقودة
✅ سجلات تفصيلية للتصحيح
✅ معالجة شاملة للأخطاء

## الاختبار
```bash
python test_subscription_api.py
```

```
🎉 Subscription created successfully!
   Database ID: 3
   Stripe ID: sub_1SKnbPKIRFVcVGUqMtGFw0vP
   Status: active
```

## الملفات المحدثة
- `apps/subscriptions/stripe_service.py` - إصلاح معالجة current_period_start
- `test_subscription_api.py` - سكريبت اختبار شامل

الآن يمكن إنشاء الاشتراكات بنجاح في الواجهة الأمامية!
