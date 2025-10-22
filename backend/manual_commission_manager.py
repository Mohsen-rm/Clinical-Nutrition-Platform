#!/usr/bin/env python
"""
مدير العمولات اليدوي - أدوات إدارة العمولات والمدفوعات
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
from apps.affiliates.models import AffiliateCommission, AffiliateStats, PayoutRequest

User = get_user_model()

class ManualCommissionManager:
    """مدير العمولات اليدوي"""
    
    def __init__(self):
        self.COMMISSION_RATE = Decimal('0.30')  # 30%
    
    def show_main_menu(self):
        """عرض القائمة الرئيسية"""
        while True:
            print("\n" + "=" * 60)
            print("🏥 مدير العمولات اليدوي - Clinical Nutrition Platform")
            print("=" * 60)
            print("1. 📊 عرض تقرير العمولات")
            print("2. 👥 عرض الشركاء وإحصائياتهم")
            print("3. 💰 عرض العمولات المعلقة")
            print("4. ✅ تحديد عمولات كمدفوعة")
            print("5. 🔍 البحث عن شريك معين")
            print("6. 📋 عرض طلبات السحب")
            print("7. ➕ إنشاء عمولة يدوياً")
            print("8. 🔄 تحديث إحصائيات الشركاء")
            print("9. 📈 تقرير مفصل لشريك")
            print("0. 🚪 خروج")
            print("-" * 60)
            
            choice = input("اختر رقم العملية: ").strip()
            
            if choice == '1':
                self.show_commission_report()
            elif choice == '2':
                self.show_affiliates_list()
            elif choice == '3':
                self.show_pending_commissions()
            elif choice == '4':
                self.mark_commissions_paid()
            elif choice == '5':
                self.search_affiliate()
            elif choice == '6':
                self.show_payout_requests()
            elif choice == '7':
                self.create_manual_commission()
            elif choice == '8':
                self.update_all_stats()
            elif choice == '9':
                self.detailed_affiliate_report()
            elif choice == '0':
                print("👋 وداعاً!")
                break
            else:
                print("❌ اختيار غير صحيح، حاول مرة أخرى")
    
    def show_commission_report(self):
        """عرض تقرير العمولات الشامل"""
        print("\n📋 تقرير العمولات الشامل")
        print("=" * 50)
        
        # إحصائيات عامة
        total_commissions = AffiliateCommission.objects.count()
        pending_commissions = AffiliateCommission.objects.filter(status='pending')
        paid_commissions = AffiliateCommission.objects.filter(status='paid')
        
        total_pending_amount = sum(c.commission_amount for c in pending_commissions)
        total_paid_amount = sum(c.commission_amount for c in paid_commissions)
        
        print(f"📊 إجمالي العمولات: {total_commissions}")
        print(f"⏳ العمولات المعلقة: {pending_commissions.count()} (${total_pending_amount:.2f})")
        print(f"✅ العمولات المدفوعة: {paid_commissions.count()} (${total_paid_amount:.2f})")
        print(f"💰 إجمالي العمولات: ${total_pending_amount + total_paid_amount:.2f}")
        
        # العمولات حسب الشهر
        print("\n📅 العمولات حسب الشهر (آخر 6 أشهر):")
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_commissions = AffiliateCommission.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            )
            month_amount = sum(c.commission_amount for c in month_commissions)
            
            print(f"  {month_start.strftime('%Y-%m')}: {month_commissions.count()} عمولة (${month_amount:.2f})")
        
        # أفضل الشركاء
        print("\n🏆 أفضل 10 شركاء:")
        top_affiliates = AffiliateStats.objects.filter(
            total_commission_earned__gt=0
        ).order_by('-total_commission_earned')[:10]
        
        for i, stats in enumerate(top_affiliates, 1):
            available = stats.total_commission_earned - stats.total_commission_paid
            print(f"{i:2d}. {stats.user.email:<30} "
                  f"إجمالي: ${stats.total_commission_earned:>8.2f} "
                  f"متاح: ${available:>8.2f} "
                  f"إحالات: {stats.total_referrals:>3d}")
    
    def show_affiliates_list(self):
        """عرض قائمة الشركاء"""
        print("\n👥 قائمة الشركاء")
        print("=" * 80)
        
        affiliates = User.objects.filter(
            affiliate_commissions__isnull=False
        ).distinct().order_by('email')
        
        if not affiliates:
            print("❌ لا يوجد شركاء حالياً")
            return
        
        print(f"{'#':<3} {'البريد الإلكتروني':<30} {'الإحالات':<8} {'العمولات':<10} {'المدفوع':<10} {'المعلق':<10}")
        print("-" * 80)
        
        for i, affiliate in enumerate(affiliates, 1):
            stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
            pending = stats.total_commission_earned - stats.total_commission_paid
            
            print(f"{i:<3} {affiliate.email:<30} "
                  f"{stats.total_referrals:<8} "
                  f"${stats.total_commission_earned:<9.2f} "
                  f"${stats.total_commission_paid:<9.2f} "
                  f"${pending:<9.2f}")
    
    def show_pending_commissions(self):
        """عرض العمولات المعلقة"""
        print("\n💰 العمولات المعلقة")
        print("=" * 100)
        
        pending_commissions = AffiliateCommission.objects.filter(
            status='pending'
        ).order_by('-created_at')
        
        if not pending_commissions:
            print("✅ لا توجد عمولات معلقة")
            return
        
        print(f"{'ID':<5} {'الشريك':<25} {'المبلغ':<10} {'النوع':<12} {'التاريخ':<12} {'المُحال':<25}")
        print("-" * 100)
        
        total_pending = Decimal('0.00')
        for commission in pending_commissions:
            total_pending += commission.commission_amount
            print(f"{commission.id:<5} "
                  f"{commission.affiliate.email:<25} "
                  f"${commission.commission_amount:<9.2f} "
                  f"{commission.commission_type:<12} "
                  f"{commission.created_at.strftime('%Y-%m-%d'):<12} "
                  f"{commission.referred_user.email:<25}")
        
        print("-" * 100)
        print(f"إجمالي العمولات المعلقة: ${total_pending:.2f}")
    
    def mark_commissions_paid(self):
        """تحديد عمولات كمدفوعة"""
        print("\n✅ تحديد العمولات كمدفوعة")
        print("=" * 50)
        
        print("اختر طريقة التحديد:")
        print("1. تحديد جميع العمولات المعلقة")
        print("2. تحديد عمولات شريك معين")
        print("3. تحديد عمولات محددة بالـ ID")
        print("4. العودة للقائمة الرئيسية")
        
        choice = input("اختر رقم العملية: ").strip()
        
        if choice == '1':
            self._mark_all_pending_paid()
        elif choice == '2':
            self._mark_affiliate_commissions_paid()
        elif choice == '3':
            self._mark_specific_commissions_paid()
        elif choice == '4':
            return
        else:
            print("❌ اختيار غير صحيح")
    
    def _mark_all_pending_paid(self):
        """تحديد جميع العمولات المعلقة كمدفوعة"""
        pending_commissions = AffiliateCommission.objects.filter(status='pending')
        total_amount = sum(c.commission_amount for c in pending_commissions)
        
        print(f"📊 سيتم تحديد {pending_commissions.count()} عمولة كمدفوعة")
        print(f"💰 إجمالي المبلغ: ${total_amount:.2f}")
        
        if pending_commissions.count() == 0:
            print("❌ لا توجد عمولات معلقة")
            return
        
        confirm = input("هل تريد المتابعة؟ (y/N): ")
        if confirm.lower() == 'y':
            with transaction.atomic():
                for commission in pending_commissions:
                    commission.status = 'paid'
                    commission.paid_at = timezone.now()
                    commission.save()
                
                # تحديث إحصائيات جميع الشركاء
                affiliates = set(c.affiliate for c in pending_commissions)
                for affiliate in affiliates:
                    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
                    stats.update_stats()
            
            print(f"✅ تم تحديد {pending_commissions.count()} عمولة كمدفوعة")
        else:
            print("❌ تم إلغاء العملية")
    
    def _mark_affiliate_commissions_paid(self):
        """تحديد عمولات شريك معين كمدفوعة"""
        email = input("أدخل بريد الشريك الإلكتروني: ").strip()
        
        try:
            affiliate = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"❌ لم يتم العثور على المستخدم: {email}")
            return
        
        pending_commissions = AffiliateCommission.objects.filter(
            affiliate=affiliate,
            status='pending'
        )
        
        if not pending_commissions:
            print(f"❌ لا توجد عمولات معلقة للشريك: {email}")
            return
        
        total_amount = sum(c.commission_amount for c in pending_commissions)
        
        print(f"📊 سيتم تحديد {pending_commissions.count()} عمولة كمدفوعة للشريك: {email}")
        print(f"💰 إجمالي المبلغ: ${total_amount:.2f}")
        
        # عرض تفاصيل العمولات
        print("\nتفاصيل العمولات:")
        for commission in pending_commissions:
            print(f"  ID: {commission.id} - ${commission.commission_amount:.2f} - {commission.created_at.strftime('%Y-%m-%d')}")
        
        confirm = input("هل تريد المتابعة؟ (y/N): ")
        if confirm.lower() == 'y':
            with transaction.atomic():
                for commission in pending_commissions:
                    commission.status = 'paid'
                    commission.paid_at = timezone.now()
                    commission.save()
                
                # تحديث إحصائيات الشريك
                stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
                stats.update_stats()
            
            print(f"✅ تم تحديد {pending_commissions.count()} عمولة كمدفوعة للشريك: {email}")
        else:
            print("❌ تم إلغاء العملية")
    
    def _mark_specific_commissions_paid(self):
        """تحديد عمولات محددة بالـ ID كمدفوعة"""
        ids_input = input("أدخل أرقام العمولات مفصولة بفاصلة (مثال: 1,2,3): ").strip()
        
        try:
            commission_ids = [int(id.strip()) for id in ids_input.split(',')]
        except ValueError:
            print("❌ تنسيق غير صحيح للأرقام")
            return
        
        commissions = AffiliateCommission.objects.filter(
            id__in=commission_ids,
            status='pending'
        )
        
        if not commissions:
            print("❌ لم يتم العثور على عمولات معلقة بهذه الأرقام")
            return
        
        total_amount = sum(c.commission_amount for c in commissions)
        
        print(f"📊 سيتم تحديد {commissions.count()} عمولة كمدفوعة")
        print(f"💰 إجمالي المبلغ: ${total_amount:.2f}")
        
        # عرض تفاصيل العمولات
        print("\nتفاصيل العمولات:")
        for commission in commissions:
            print(f"  ID: {commission.id} - {commission.affiliate.email} - ${commission.commission_amount:.2f}")
        
        confirm = input("هل تريد المتابعة؟ (y/N): ")
        if confirm.lower() == 'y':
            with transaction.atomic():
                for commission in commissions:
                    commission.status = 'paid'
                    commission.paid_at = timezone.now()
                    commission.save()
                
                # تحديث إحصائيات الشركاء
                affiliates = set(c.affiliate for c in commissions)
                for affiliate in affiliates:
                    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
                    stats.update_stats()
            
            print(f"✅ تم تحديد {commissions.count()} عمولة كمدفوعة")
        else:
            print("❌ تم إلغاء العملية")
    
    def search_affiliate(self):
        """البحث عن شريك معين"""
        email = input("أدخل بريد الشريك الإلكتروني: ").strip()
        
        try:
            affiliate = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"❌ لم يتم العثور على المستخدم: {email}")
            return
        
        print(f"\n🔍 تفاصيل الشريك: {email}")
        print("=" * 60)
        
        # الإحصائيات
        stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
        
        print(f"📊 إجمالي الإحالات: {stats.total_referrals}")
        print(f"🟢 الإحالات النشطة: {stats.active_referrals}")
        print(f"💰 إجمالي العمولات: ${stats.total_commission_earned:.2f}")
        print(f"✅ العمولات المدفوعة: ${stats.total_commission_paid:.2f}")
        print(f"⏳ العمولات المعلقة: ${stats.total_commission_pending:.2f}")
        
        # العمولات الأخيرة
        recent_commissions = AffiliateCommission.objects.filter(
            affiliate=affiliate
        ).order_by('-created_at')[:10]
        
        if recent_commissions:
            print(f"\n📋 آخر {len(recent_commissions)} عمولات:")
            print(f"{'ID':<5} {'المبلغ':<10} {'الحالة':<10} {'التاريخ':<12} {'المُحال':<25}")
            print("-" * 70)
            
            for commission in recent_commissions:
                print(f"{commission.id:<5} "
                      f"${commission.commission_amount:<9.2f} "
                      f"{commission.status:<10} "
                      f"{commission.created_at.strftime('%Y-%m-%d'):<12} "
                      f"{commission.referred_user.email:<25}")
    
    def show_payout_requests(self):
        """عرض طلبات السحب"""
        print("\n📋 طلبات السحب")
        print("=" * 80)
        
        payout_requests = PayoutRequest.objects.all().order_by('-created_at')
        
        if not payout_requests:
            print("❌ لا توجد طلبات سحب")
            return
        
        print(f"{'ID':<5} {'الشريك':<25} {'المبلغ':<10} {'الحالة':<12} {'التاريخ':<12} {'الطريقة':<15}")
        print("-" * 80)
        
        for request in payout_requests:
            print(f"{request.id:<5} "
                  f"{request.affiliate.email:<25} "
                  f"${request.amount:<9.2f} "
                  f"{request.status:<12} "
                  f"{request.created_at.strftime('%Y-%m-%d'):<12} "
                  f"{request.payment_method:<15}")
    
    def create_manual_commission(self):
        """إنشاء عمولة يدوياً"""
        print("\n➕ إنشاء عمولة يدوياً")
        print("=" * 50)
        
        # اختيار الشريك
        affiliate_email = input("بريد الشريك الإلكتروني: ").strip()
        try:
            affiliate = User.objects.get(email=affiliate_email)
        except User.DoesNotExist:
            print(f"❌ لم يتم العثور على المستخدم: {affiliate_email}")
            return
        
        # اختيار المستخدم المُحال
        referred_email = input("بريد المستخدم المُحال: ").strip()
        try:
            referred_user = User.objects.get(email=referred_email)
        except User.DoesNotExist:
            print(f"❌ لم يتم العثور على المستخدم: {referred_email}")
            return
        
        # المبلغ
        try:
            amount = Decimal(input("مبلغ العمولة: $").strip())
        except:
            print("❌ مبلغ غير صحيح")
            return
        
        # الملاحظات
        notes = input("ملاحظات (اختياري): ").strip()
        
        print(f"\n📋 تأكيد إنشاء العمولة:")
        print(f"الشريك: {affiliate_email}")
        print(f"المُحال: {referred_email}")
        print(f"المبلغ: ${amount:.2f}")
        print(f"الملاحظات: {notes or 'لا توجد'}")
        
        confirm = input("هل تريد إنشاء العمولة؟ (y/N): ")
        if confirm.lower() == 'y':
            commission = AffiliateCommission.objects.create(
                affiliate=affiliate,
                referred_user=referred_user,
                payment=None,  # عمولة يدوية
                commission_amount=amount,
                commission_percentage=self.COMMISSION_RATE * 100,
                commission_type='one_time',
                status='pending',
                notes=notes
            )
            
            # تحديث إحصائيات الشريك
            stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
            stats.update_stats()
            
            print(f"✅ تم إنشاء العمولة بنجاح: ID {commission.id}")
        else:
            print("❌ تم إلغاء العملية")
    
    def update_all_stats(self):
        """تحديث إحصائيات جميع الشركاء"""
        print("\n🔄 تحديث إحصائيات الشركاء...")
        
        affiliates = User.objects.filter(
            affiliate_commissions__isnull=False
        ).distinct()
        
        updated_count = 0
        for affiliate in affiliates:
            stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
            stats.update_stats()
            updated_count += 1
            
            if created:
                print(f"➕ تم إنشاء إحصائيات جديدة: {affiliate.email}")
            else:
                print(f"🔄 تم تحديث إحصائيات: {affiliate.email}")
        
        print(f"✅ تم تحديث إحصائيات {updated_count} شريك")
    
    def detailed_affiliate_report(self):
        """تقرير مفصل لشريك"""
        email = input("أدخل بريد الشريك الإلكتروني: ").strip()
        
        try:
            affiliate = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"❌ لم يتم العثور على المستخدم: {email}")
            return
        
        print(f"\n📈 تقرير مفصل للشريك: {email}")
        print("=" * 80)
        
        # الإحصائيات العامة
        stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
        
        print(f"📊 الإحصائيات العامة:")
        print(f"  إجمالي الإحالات: {stats.total_referrals}")
        print(f"  الإحالات النشطة: {stats.active_referrals}")
        print(f"  إجمالي العمولات: ${stats.total_commission_earned:.2f}")
        print(f"  العمولات المدفوعة: ${stats.total_commission_paid:.2f}")
        print(f"  العمولات المعلقة: ${stats.total_commission_pending:.2f}")
        
        # الإحالات
        referrals = User.objects.filter(referred_by=affiliate)
        if referrals:
            print(f"\n👥 الإحالات ({referrals.count()}):")
            for referral in referrals:
                subscription_status = "غير مشترك"
                if hasattr(referral, 'subscription'):
                    subscription_status = referral.subscription.status
                
                print(f"  {referral.email} - {subscription_status}")
        
        # العمولات حسب الشهر
        print(f"\n📅 العمولات حسب الشهر (آخر 12 شهر):")
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_commissions = AffiliateCommission.objects.filter(
                affiliate=affiliate,
                created_at__gte=month_start,
                created_at__lte=month_end
            )
            month_amount = sum(c.commission_amount for c in month_commissions)
            
            if month_commissions.count() > 0:
                print(f"  {month_start.strftime('%Y-%m')}: {month_commissions.count()} عمولة (${month_amount:.2f})")

def main():
    """الدالة الرئيسية"""
    manager = ManualCommissionManager()
    manager.show_main_menu()

if __name__ == '__main__':
    main()
