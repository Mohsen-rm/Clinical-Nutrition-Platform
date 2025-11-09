#!/usr/bin/env python
"""
Quick commands for managing commissions
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
    """Show commission summary"""
    print("📊 Quick commission summary")
    print("=" * 40)
    
    total = AffiliateCommission.objects.count()
    pending = AffiliateCommission.objects.filter(status='pending')
    paid = AffiliateCommission.objects.filter(status='paid')
    
    pending_amount = sum(c.commission_amount for c in pending)
    paid_amount = sum(c.commission_amount for c in paid)
    
    print(f"Total commissions: {total}")
    print(f"Pending: {pending.count()} (${pending_amount:.2f})")
    print(f"Paid: {paid.count()} (${paid_amount:.2f})")
    
    if pending.count() > 0:
        print(f"\n💰 Pending commissions:")
        for commission in pending:
            print(f"  ID {commission.id}: {commission.affiliate.email} - ${commission.commission_amount}")

def pay_all_pending():
    """Pay all pending commissions"""
    pending = AffiliateCommission.objects.filter(status='pending')
    
    if not pending:
        print("✅ No pending commissions")
        return
    
    total_amount = sum(c.commission_amount for c in pending)
    print(f"💳 Will pay {pending.count()} commissions totaling ${total_amount:.2f}")
    
    for commission in pending:
        commission.status = 'paid'
        commission.paid_at = timezone.now()
        commission.save()
        print(f"✅ Paid commission {commission.id}: {commission.affiliate.email} - ${commission.commission_amount}")
    
    # Update stats
    affiliates = set(c.affiliate for c in pending)
    for affiliate in affiliates:
        stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
    
    print(f"✅ All pending commissions paid")

def pay_affiliate_commissions(email):
    """Pay commissions for a specific affiliate"""
    try:
        affiliate = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"❌ Affiliate not found: {email}")
        return
    
    pending = AffiliateCommission.objects.filter(
        affiliate=affiliate,
        status='pending'
    )
    
    if not pending:
        print(f"✅ No pending commissions for affiliate: {email}")
        return
    
    total_amount = sum(c.commission_amount for c in pending)
    print(f"💳 Will pay {pending.count()} commissions to affiliate {email} totaling ${total_amount:.2f}")
    
    for commission in pending:
        commission.status = 'paid'
        commission.paid_at = timezone.now()
        commission.save()
        print(f"✅ Paid commission {commission.id}: ${commission.commission_amount}")
    
    # Update stats
    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
    stats.update_stats()
    
    print(f"✅ Paid all commissions for affiliate: {email}")

def show_affiliate_details(email):
    """Show affiliate details"""
    try:
        affiliate = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"❌ Affiliate not found: {email}")
        return
    
    print(f"👤 Affiliate details: {email}")
    print("=" * 40)
    
    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
    stats.update_stats()
    
    print(f"Total commissions: ${stats.total_commission_earned:.2f}")
    print(f"Paid commissions: ${stats.total_commission_paid:.2f}")
    print(f"Pending commissions: ${stats.total_commission_pending:.2f}")
    print(f"Total referrals: {stats.total_referrals}")
    
    # Recent commissions
    recent = AffiliateCommission.objects.filter(
        affiliate=affiliate
    ).order_by('-created_at')[:5]
    
    if recent:
        print(f"\nLast {len(recent)} commissions:")
        for commission in recent:
            print(f"  ${commission.commission_amount:.2f} - {commission.status} - {commission.created_at.strftime('%Y-%m-%d')}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Available commands:")
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
        print("❌ Invalid command")

if __name__ == '__main__':
    main()
