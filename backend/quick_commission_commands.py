#!/usr/bin/env python
"""
أوامر سريعة لإدارة العمولات
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
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

def show_commission_summary():
    """عرض ملخص العمولات"""
    print("📊 ملخص العمولات السريع")
    print("=" * 40)
    
    total = AffiliateCommission.objects.count()
    pending = AffiliateCommission.objects.filter(status='pending')
    paid = AffiliateCommission.objects.filter(status='paid')
    
    pending_amount = sum(c.commission_amount for c in pending)
    paid_amount = sum(c.commission_amount for c in paid)
    
    print(f"إجمالي العمولات: {total}")
    print(f"المعلقة: {pending.count()} (${pending_amount:.2f})")
    print(f"المدفوعة: {paid.count()} (${paid_amount:.2f})")
    
    if pending.count() > 0:
        print(f"\n💰 العمولات المعلقة:")
        for commission in pending:
            print(f"  ID {commission.id}: {commission.affiliate.email} - ${commission.commission_amount}")

def pay_all_pending():
    """دفع جميع العمولات المعلقة"""
    pending = AffiliateCommission.objects.filter(status='pending')
    
    if not pending:
        print("✅ لا توجد عمولات معلقة")
        return
    
    total_amount = sum(c.commission_amount for c in pending)
    print(f"💳 سيتم دفع {pending.count()} عمولة بقيمة ${total_amount:.2f}")
    
    for commission in pending:
        commission.status = 'paid'
        commission.paid_at = timezone.now()
        commission.save()
        print(f"✅ تم دفع عمولة {commission.id}: {commission.affiliate.email} - ${commission.commission_amount}")
    
    # تحديث الإحصائيات
    affiliates = set(c.affiliate for c in pending)
    for affiliate in affiliates:
        stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
    
    print(f"✅ تم دفع جميع العمولات المعلقة")

def pay_affiliate_commissions(email):
    """دفع عمولات شريك معين"""
    try:
        affiliate = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"❌ لم يتم العثور على الشريك: {email}")
        return
    
    pending = AffiliateCommission.objects.filter(
        affiliate=affiliate,
        status='pending'
    )
    
    if not pending:
        print(f"✅ لا توجد عمولات معلقة للشريك: {email}")
        return
    
    total_amount = sum(c.commission_amount for c in pending)
    print(f"💳 سيتم دفع {pending.count()} عمولة للشريك {email} بقيمة ${total_amount:.2f}")
    
    for commission in pending:
        commission.status = 'paid'
        commission.paid_at = timezone.now()
        commission.save()
        print(f"✅ تم دفع عمولة {commission.id}: ${commission.commission_amount}")
    
    # تحديث الإحصائيات
    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
    stats.update_stats()
    
    print(f"✅ تم دفع جميع عمولات الشريك: {email}")

def show_affiliate_details(email):
    """عرض تفاصيل شريك"""
    try:
        affiliate = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"❌ لم يتم العثور على الشريك: {email}")
        return
    
    print(f"👤 تفاصيل الشريك: {email}")
    print("=" * 40)
    
    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
    stats.update_stats()
    
    print(f"إجمالي العمولات: ${stats.total_commission_earned:.2f}")
    print(f"العمولات المدفوعة: ${stats.total_commission_paid:.2f}")
    print(f"العمولات المعلقة: ${stats.total_commission_pending:.2f}")
    print(f"إجمالي الإحالات: {stats.total_referrals}")
    
    # العمولات الأخيرة
    recent = AffiliateCommission.objects.filter(
        affiliate=affiliate
    ).order_by('-created_at')[:5]
    
    if recent:
        print(f"\nآخر {len(recent)} عمولات:")
        for commission in recent:
            print(f"  ${commission.commission_amount:.2f} - {commission.status} - {commission.created_at.strftime('%Y-%m-%d')}")

def main():
    """الدالة الرئيسية"""
    if len(sys.argv) < 2:
        print("الأوامر المتاحة:")
        print("  python quick_commission_commands.py summary")
        print("  python quick_commission_commands.py pay_all")
        print("  python quick_commission_commands.py pay <email>")
        print("  python quick_commission_commands.py details <email>")
        return
    
    command = sys.argv[1]
    
    if command == 'summary':
        show_commission_summary()
    elif command == 'pay_all':
        pay_all_pending()
    elif command == 'pay' and len(sys.argv) > 2:
        email = sys.argv[2]
        pay_affiliate_commissions(email)
    elif command == 'details' and len(sys.argv) > 2:
        email = sys.argv[2]
        show_affiliate_details(email)
    else:
        print("❌ أمر غير صحيح")

if __name__ == '__main__':
    main()
