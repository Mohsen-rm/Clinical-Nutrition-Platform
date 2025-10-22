#!/usr/bin/env python
"""
إنشاء بيانات تجريبية للعمولات لاختبار النظام
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.subscriptions.models import Payment, Subscription, SubscriptionPlan
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

def create_test_commissions():
    """إنشاء عمولات تجريبية"""
    print("🚀 إنشاء بيانات تجريبية للعمولات...")
    
    try:
        # الحصول على المستخدمين
        admin = User.objects.get(email='admin@example.com')
        doctor = User.objects.get(email='doctor@example.com')
        patient = User.objects.get(email='patient@example.com')
        
        # الحصول على خطة اشتراك
        basic_plan = SubscriptionPlan.objects.filter(name__icontains='basic').first()
        if not basic_plan:
            print("❌ لم يتم العثور على خطة Basic")
            return
        
        print(f"📋 استخدام خطة: {basic_plan.name} - ${basic_plan.price}")
        
        # إنشاء اشتراكات تجريبية إذا لم تكن موجودة
        subscription1, created = Subscription.objects.get_or_create(
            user=patient,
            defaults={
                'plan': basic_plan,
                'stripe_subscription_id': 'sub_test_001',
                'status': 'active',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timezone.timedelta(days=30),
            }
        )
        
        if created:
            print(f"✅ تم إنشاء اشتراك جديد للمريض")
        
        # إنشاء مدفوعات تجريبية
        payments_data = [
            {
                'subscription': subscription1,
                'amount': Decimal('29.00'),
                'stripe_payment_intent_id': 'pi_test_001',
                'status': 'succeeded',
                'affiliate_commission': None,  # لم تتم معالجة العمولة بعد
            },
            {
                'subscription': subscription1,
                'amount': Decimal('29.00'),
                'stripe_payment_intent_id': 'pi_test_002',
                'status': 'succeeded',
                'affiliate_commission': None,
            },
        ]
        
        created_payments = []
        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(
                stripe_payment_intent_id=payment_data['stripe_payment_intent_id'],
                defaults=payment_data
            )
            if created:
                created_payments.append(payment)
                print(f"✅ تم إنشاء مدفوعة: {payment.stripe_payment_intent_id} - ${payment.amount}")
        
        # تعيين المريض كمُحال من المدير
        if not patient.referred_by:
            patient.referred_by = admin
            patient.save()
            print(f"✅ تم تعيين {patient.email} كمُحال من {admin.email}")
        
        # إنشاء عمولات تجريبية يدوياً
        commission_data = [
            {
                'affiliate': admin,
                'referred_user': patient,
                'payment': created_payments[0] if created_payments else None,
                'commission_amount': Decimal('8.70'),  # 30% من $29
                'commission_percentage': Decimal('30.00'),
                'commission_type': 'subscription',
                'status': 'pending',
                'notes': 'عمولة تجريبية - اشتراك شهري'
            },
            {
                'affiliate': admin,
                'referred_user': patient,
                'payment': created_payments[1] if len(created_payments) > 1 else None,
                'commission_amount': Decimal('8.70'),  # 30% من $29
                'commission_percentage': Decimal('30.00'),
                'commission_type': 'subscription',
                'status': 'pending',
                'notes': 'عمولة تجريبية - تجديد شهري'
            },
            {
                'affiliate': doctor,
                'referred_user': patient,
                'payment': None,  # عمولة يدوية
                'commission_amount': Decimal('15.00'),
                'commission_percentage': Decimal('30.00'),
                'commission_type': 'one_time',
                'status': 'paid',
                'paid_at': timezone.now(),
                'notes': 'عمولة يدوية - مكافأة خاصة'
            },
        ]
        
        created_commissions = []
        for comm_data in commission_data:
            # التحقق من عدم وجود العمولة مسبقاً
            existing = AffiliateCommission.objects.filter(
                affiliate=comm_data['affiliate'],
                referred_user=comm_data['referred_user'],
                commission_amount=comm_data['commission_amount'],
                commission_type=comm_data['commission_type']
            ).first()
            
            if not existing:
                commission = AffiliateCommission.objects.create(**comm_data)
                created_commissions.append(commission)
                print(f"✅ تم إنشاء عمولة: {commission.affiliate.email} - ${commission.commission_amount} ({commission.status})")
        
        # تحديث إحصائيات الشركاء
        for affiliate in [admin, doctor]:
            stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
            stats.update_stats()
            if created:
                print(f"✅ تم إنشاء إحصائيات جديدة: {affiliate.email}")
            else:
                print(f"🔄 تم تحديث إحصائيات: {affiliate.email}")
        
        print(f"\n📊 ملخص البيانات المُنشأة:")
        print(f"💳 المدفوعات: {len(created_payments)}")
        print(f"💰 العمولات: {len(created_commissions)}")
        
        # عرض الإحصائيات
        print(f"\n📈 إحصائيات الشركاء:")
        for affiliate in [admin, doctor]:
            stats = AffiliateStats.objects.get(user=affiliate)
            print(f"{affiliate.email}:")
            print(f"  إجمالي العمولات: ${stats.total_commission_earned}")
            print(f"  العمولات المدفوعة: ${stats.total_commission_paid}")
            print(f"  العمولات المعلقة: ${stats.total_commission_pending}")
            print(f"  إجمالي الإحالات: {stats.total_referrals}")
        
        print("\n✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_commissions()
