#!/usr/bin/env python
"""
Fix commission processing - ensure payments are linked to commissions
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from apps.subscriptions.models import Payment, Subscription
from apps.affiliates.models import AffiliateCommission, AffiliateStats
from decimal import Decimal

User = get_user_model()

def fix_missing_commissions():
    """Fix missing commissions for successful payments"""
    print("🔍 Searching for successful payments without commissions...")
    
    # Find successful payments for referred users without commissions
    payments_without_commissions = Payment.objects.filter(
        status='succeeded',
        subscription__user__referred_by__isnull=False
    ).exclude(
        commissions__isnull=False
    ).select_related(
        'subscription__user__referred_by',
        'subscription__plan'
    )
    
    print(f"📊 Found {payments_without_commissions.count()} payments needing processing")
    
    fixed_count = 0
    total_commission = Decimal('0.00')
    
    for payment in payments_without_commissions:
        try:
            with transaction.atomic():
                subscription = payment.subscription
                referred_user = subscription.user
                affiliate = referred_user.referred_by
                
                if not affiliate:
                    continue
                
                # Calculate commission (30%)
                commission_amount = payment.amount * Decimal('0.30')
                
                # Create commission record
                commission = AffiliateCommission.objects.create(
                    affiliate=affiliate,
                    referred_user=referred_user,
                    payment=payment,
                    commission_amount=commission_amount,
                    commission_percentage=Decimal('30.00'),
                    commission_type='subscription',
                    status='pending'
                )
                
                # Update payment
                payment.affiliate_commission = commission_amount
                payment.save()
                
                # Update affiliate stats
                stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
                stats.update_stats()
                
                fixed_count += 1
                total_commission += commission_amount
                
                print(f"✅ Created commission: {affiliate.email} - ${commission_amount}")
                
        except Exception as e:
            print(f"❌ Error processing payment {payment.id}: {str(e)}")
    
    print(f"\n📋 Results:")
    print(f"✅ Fixed {fixed_count} commissions")
    print(f"💰 Total commissions created: ${total_commission}")

def verify_affiliate_setup():
    """Verify affiliate system setup"""
    print("\n🔍 Verifying affiliate system setup:")
    print("=" * 50)
    
    # Check users with referral codes
    users_with_codes = User.objects.filter(referral_code__isnull=False).exclude(referral_code='')
    print(f"👥 Users with referral codes: {users_with_codes.count()}")
    
    for user in users_with_codes[:5]:  # first 5 users
        print(f"  {user.email}: {user.referral_code}")
    
    # Check referred users
    referred_users = User.objects.filter(referred_by__isnull=False)
    print(f"👥 Referred users: {referred_users.count()}")
    
    for user in referred_users[:5]:  # first 5 users
        print(f"  {user.email} ← {user.referred_by.email}")
    
    # Check active subscriptions for referred users
    active_subscriptions = Subscription.objects.filter(
        user__referred_by__isnull=False,
        status__in=['active', 'trialing']
    )
    print(f"📋 Active subscriptions for referred users: {active_subscriptions.count()}")
    
    # Check payments
    payments = Payment.objects.filter(
        subscription__user__referred_by__isnull=False,
        status='succeeded'
    )
    print(f"💳 Successful payments for referred users: {payments.count()}")
    
    # Check commissions
    commissions = AffiliateCommission.objects.all()
    print(f"💰 Total commissions: {commissions.count()}")
    
    pending_commissions = AffiliateCommission.objects.filter(status='pending')
    paid_commissions = AffiliateCommission.objects.filter(status='paid')
    
    print(f"⏳ Pending commissions: {pending_commissions.count()}")
    print(f"✅ Paid commissions: {paid_commissions.count()}")

def main():
    """Main function"""
    print("🚀 Starting commission processing fix")
    print("=" * 50)
    
    # Verify setup
    verify_affiliate_setup()
    
    # Fix missing commissions
    fix_missing_commissions()
    
    print("\n✅ Fix completed")

if __name__ == '__main__':
    main()
