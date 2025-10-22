#!/usr/bin/env python
"""
سكريبت معالجة العمولات التلقائي - نظام الشراكة 30%
يتم تشغيله تلقائياً أو يدوياً لمعالجة العمولات المستحقة
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from apps.subscriptions.models import Payment, Subscription
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

class AffiliateCommissionProcessor:
    """معالج العمولات التلقائي"""
    
    COMMISSION_RATE = Decimal('0.30')  # 30%
    
    def __init__(self):
        self.processed_count = 0
        self.total_commission_amount = Decimal('0.00')
        self.errors = []
    
    def process_new_payments(self):
        """معالجة المدفوعات الجديدة التي لم تتم معالجة عمولاتها"""
        print("🔍 البحث عن مدفوعات جديدة لمعالجة العمولات...")
        
        # البحث عن المدفوعات الناجحة التي لم تتم معالجة عمولاتها
        new_payments = Payment.objects.filter(
            status='succeeded',
            affiliate_commission__isnull=True,  # لم تتم معالجة العمولة
            subscription__user__referred_by__isnull=False  # المستخدم تم إحالته
        ).select_related(
            'subscription__user__referred_by',
            'subscription__plan'
        )
        
        print(f"📊 تم العثور على {new_payments.count()} مدفوعة جديدة")
        
        for payment in new_payments:
            try:
                self._process_payment_commission(payment)
            except Exception as e:
                error_msg = f"خطأ في معالجة المدفوعة {payment.id}: {str(e)}"
                self.errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return self.processed_count
    
    def _process_payment_commission(self, payment):
        """معالجة عمولة مدفوعة واحدة"""
        with transaction.atomic():
            subscription = payment.subscription
            referred_user = subscription.user
            affiliate = referred_user.referred_by
            
            if not affiliate:
                return
            
            # حساب العمولة (30% من المبلغ)
            commission_amount = payment.amount * self.COMMISSION_RATE
            
            print(f"💰 معالجة عمولة: {affiliate.email}")
            print(f"   المبلغ الأصلي: ${payment.amount}")
            print(f"   العمولة (30%): ${commission_amount}")
            
            # إنشاء سجل العمولة
            commission = AffiliateCommission.objects.create(
                affiliate=affiliate,
                referred_user=referred_user,
                payment=payment,
                commission_amount=commission_amount,
                commission_percentage=self.COMMISSION_RATE * 100,
                commission_type='subscription',
                status='pending'
            )
            
            # تحديث المدفوعة لتسجيل العمولة
            payment.affiliate_commission = commission_amount
            payment.save()
            
            # تحديث إحصائيات الشريك
            self._update_affiliate_stats(affiliate)
            
            self.processed_count += 1
            self.total_commission_amount += commission_amount
            
            print(f"✅ تم إنشاء العمولة بنجاح: ID {commission.id}")
    
    def _update_affiliate_stats(self, affiliate):
        """تحديث إحصائيات الشريك"""
        stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
        
        if created:
            print(f"📊 تم إنشاء إحصائيات جديدة للشريك: {affiliate.email}")
        else:
            print(f"📊 تم تحديث إحصائيات الشريك: {affiliate.email}")
    
    def process_recurring_commissions(self):
        """معالجة العمولات المتكررة للاشتراكات النشطة"""
        print("\n🔄 معالجة العمولات المتكررة...")
        
        # البحث عن الاشتراكات النشطة التي لها شركاء
        active_subscriptions = Subscription.objects.filter(
            status__in=['active', 'trialing'],
            user__referred_by__isnull=False
        ).select_related('user__referred_by', 'plan')
        
        print(f"📊 تم العثور على {active_subscriptions.count()} اشتراك نشط مع شركاء")
        
        # معالجة المدفوعات الجديدة لهذه الاشتراكات
        for subscription in active_subscriptions:
            recent_payments = Payment.objects.filter(
                subscription=subscription,
                status='succeeded',
                affiliate_commission__isnull=True,
                created_at__gte=timezone.now() - timedelta(days=32)  # آخر شهر
            )
            
            for payment in recent_payments:
                try:
                    self._process_payment_commission(payment)
                except Exception as e:
                    error_msg = f"خطأ في معالجة العمولة المتكررة للاشتراك {subscription.id}: {str(e)}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
    
    def mark_commissions_as_paid(self, affiliate_email=None, commission_ids=None):
        """تحديد العمولات كمدفوعة (للاستخدام اليدوي)"""
        print("\n💳 تحديد العمولات كمدفوعة...")
        
        query = AffiliateCommission.objects.filter(status='pending')
        
        if affiliate_email:
            query = query.filter(affiliate__email=affiliate_email)
            print(f"🎯 تصفية للشريك: {affiliate_email}")
        
        if commission_ids:
            query = query.filter(id__in=commission_ids)
            print(f"🎯 تصفية للعمولات: {commission_ids}")
        
        commissions = query.all()
        total_amount = sum(c.commission_amount for c in commissions)
        
        print(f"📊 سيتم تحديد {len(commissions)} عمولة كمدفوعة")
        print(f"💰 إجمالي المبلغ: ${total_amount}")
        
        if len(commissions) > 0:
            confirm = input("هل تريد المتابعة؟ (y/N): ")
            if confirm.lower() == 'y':
                with transaction.atomic():
                    for commission in commissions:
                        commission.status = 'paid'
                        commission.paid_at = timezone.now()
                        commission.save()
                        
                        # تحديث إحصائيات الشريك
                        self._update_affiliate_stats(commission.affiliate)
                
                print(f"✅ تم تحديد {len(commissions)} عمولة كمدفوعة")
            else:
                print("❌ تم إلغاء العملية")
    
    def generate_commission_report(self):
        """إنشاء تقرير العمولات"""
        print("\n📋 تقرير العمولات:")
        print("=" * 50)
        
        # إحصائيات عامة
        total_commissions = AffiliateCommission.objects.count()
        pending_commissions = AffiliateCommission.objects.filter(status='pending').count()
        paid_commissions = AffiliateCommission.objects.filter(status='paid').count()
        
        total_pending_amount = sum(
            c.commission_amount for c in AffiliateCommission.objects.filter(status='pending')
        )
        total_paid_amount = sum(
            c.commission_amount for c in AffiliateCommission.objects.filter(status='paid')
        )
        
        print(f"📊 إجمالي العمولات: {total_commissions}")
        print(f"⏳ العمولات المعلقة: {pending_commissions} (${total_pending_amount})")
        print(f"✅ العمولات المدفوعة: {paid_commissions} (${total_paid_amount})")
        
        # أفضل الشركاء
        print("\n🏆 أفضل الشركاء:")
        top_affiliates = AffiliateStats.objects.filter(
            total_commission_earned__gt=0
        ).order_by('-total_commission_earned')[:5]
        
        for i, stats in enumerate(top_affiliates, 1):
            print(f"{i}. {stats.user.email}: ${stats.total_commission_earned} "
                  f"({stats.total_referrals} إحالات)")
        
        # العمولات المعلقة حسب الشريك
        print("\n💰 العمولات المعلقة حسب الشريك:")
        pending_by_affiliate = {}
        for commission in AffiliateCommission.objects.filter(status='pending'):
            email = commission.affiliate.email
            if email not in pending_by_affiliate:
                pending_by_affiliate[email] = Decimal('0.00')
            pending_by_affiliate[email] += commission.commission_amount
        
        for email, amount in sorted(pending_by_affiliate.items(), key=lambda x: x[1], reverse=True):
            print(f"  {email}: ${amount}")
    
    def print_summary(self):
        """طباعة ملخص العملية"""
        print("\n" + "=" * 50)
        print("📋 ملخص معالجة العمولات:")
        print(f"✅ تم معالجة: {self.processed_count} عمولة")
        print(f"💰 إجمالي العمولات: ${self.total_commission_amount}")
        
        if self.errors:
            print(f"❌ الأخطاء: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("✅ لا توجد أخطاء")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء معالجة العمولات التلقائي")
    print(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    processor = AffiliateCommissionProcessor()
    
    # معالجة المدفوعات الجديدة
    processor.process_new_payments()
    
    # معالجة العمولات المتكررة
    processor.process_recurring_commissions()
    
    # إنشاء التقرير
    processor.generate_commission_report()
    
    # طباعة الملخص
    processor.print_summary()
    
    print("\n✅ انتهت معالجة العمولات")

if __name__ == '__main__':
    # التحقق من المعاملات
    if len(sys.argv) > 1:
        command = sys.argv[1]
        processor = AffiliateCommissionProcessor()
        
        if command == 'report':
            processor.generate_commission_report()
        elif command == 'pay':
            if len(sys.argv) > 2:
                affiliate_email = sys.argv[2]
                processor.mark_commissions_as_paid(affiliate_email=affiliate_email)
            else:
                processor.mark_commissions_as_paid()
        else:
            print("الأوامر المتاحة:")
            print("  python process_affiliate_commissions.py - معالجة العمولات")
            print("  python process_affiliate_commissions.py report - تقرير العمولات")
            print("  python process_affiliate_commissions.py pay [email] - تحديد العمولات كمدفوعة")
    else:
        main()
