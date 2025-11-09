#!/usr/bin/env python
"""
Affiliate system monitor - for daily operation
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.subscriptions.models import Payment, Subscription
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

def daily_affiliate_report():
    """Daily affiliate system report"""
    print(f"📅 Affiliate system report - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    # General statistics
    total_affiliates = User.objects.filter(referral_code__isnull=False).exclude(referral_code='').count()
    total_referred = User.objects.filter(referred_by__isnull=False).count()
    total_commissions = AffiliateCommission.objects.count()
    
    print(f"👥 Total affiliates: {total_affiliates}")
    print(f"👥 Total referred users: {total_referred}")
    print(f"💰 Total commissions: {total_commissions}")
    
    # Last 24 hours stats
    last_24h = timezone.now() - timedelta(hours=24)
    
    new_referrals = User.objects.filter(
        referred_by__isnull=False,
        date_joined__gte=last_24h
    ).count()
    
    new_payments = Payment.objects.filter(
        status='succeeded',
        subscription__user__referred_by__isnull=False,
        created_at__gte=last_24h
    ).count()
    
    new_commissions = AffiliateCommission.objects.filter(
        created_at__gte=last_24h
    ).count()
    
    print(f"\n📊 Last 24 hours:")
    print(f"  New referrals: {new_referrals}")
    print(f"  New payments: {new_payments}")
    print(f"  New commissions: {new_commissions}")
    
    # Warnings
    warnings = []
    
    # Warning: Payments without commissions
    payments_without_commissions = Payment.objects.filter(
        status='succeeded',
        subscription__user__referred_by__isnull=False,
        commissions__isnull=True
    ).count()
    
    if payments_without_commissions > 0:
        warnings.append(f"⚠️  {payments_without_commissions} payments without commissions")
    
    # Warning: Long-pending commissions
    old_pending = AffiliateCommission.objects.filter(
        status='pending',
        created_at__lt=timezone.now() - timedelta(days=30)
    ).count()
    
    if old_pending > 0:
        warnings.append(f"⚠️  {old_pending} commissions pending for more than 30 days")
    
    if warnings:
        print(f"\n🚨 Warnings:")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print(f"\n✅ No warnings")
    
    # Top affiliates
    print(f"\n🏆 Top 5 affiliates:")
    top_affiliates = AffiliateStats.objects.filter(
        total_commission_earned__gt=0
    ).order_by('-total_commission_earned')[:5]
    
    for i, stats in enumerate(top_affiliates, 1):
        print(f"  {i}. {stats.user.email}: ${stats.total_commission_earned} ({stats.total_referrals} referrals)")

def check_system_health():
    """Check system health"""
    print(f"\n🔍 Checking system health:")
    print("=" * 30)
    
    issues = []
    
    # Check 1: Are referral codes generated for new users?
    users_without_codes = User.objects.filter(
        referral_code__isnull=True
    ).exclude(referral_code='').count()
    
    if users_without_codes > 0:
        issues.append(f"❌ {users_without_codes} users without referral code")
    
    # Check 2: Are commissions processed for new payments?
    recent_payments = Payment.objects.filter(
        status='succeeded',
        subscription__user__referred_by__isnull=False,
        created_at__gte=timezone.now() - timedelta(hours=2)
    )
    
    unprocessed_payments = 0
    for payment in recent_payments:
        if not payment.commissions.exists():
            unprocessed_payments += 1
    
    if unprocessed_payments > 0:
        issues.append(f"❌ {unprocessed_payments} recent payments without commissions")
    
    # Check 3: Are stats up to date?
    outdated_stats = AffiliateStats.objects.filter(
        last_updated__lt=timezone.now() - timedelta(days=1)
    ).count()
    
    if outdated_stats > 0:
        issues.append(f"⚠️  {outdated_stats} affiliate stats outdated")
    
    if issues:
        print("🚨 Issues detected:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n💡 Suggested fixes:")
        if users_without_codes > 0:
            print("  - Run: python manage.py shell -c \"from apps.accounts.models import User; import uuid; [setattr(u, 'referral_code', str(uuid.uuid4())[:8].upper()) or u.save() for u in User.objects.filter(referral_code__isnull=True)]\"")
        
        if unprocessed_payments > 0:
            print("  - Run: python fix_commission_processing.py")
        
        if outdated_stats > 0:
            print("  - Run: python quick_commission_commands.py summary")
    else:
        print("✅ System is healthy")

def main():
    """Main function"""
    daily_affiliate_report()
    check_system_health()
    
    print(f"\n📋 Daily recommendations:")
    print("1. Review warnings and issues above")
    print("2. Run process_affiliate_commissions.py if needed")
    print("3. Monitor Stripe Webhook logs")

if __name__ == '__main__':
    main()
