#!/usr/bin/env python
"""
Check new referrals and fix Anonymous User issue
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

def check_recent_users():
    """Check users registered in the last 24 hours"""
    print('🔍 Checking users registered in the last 24 hours:')
    print('=' * 50)
    
    # Last 24 hours
    last_24h = timezone.now() - timedelta(hours=24)
    recent_users = User.objects.filter(date_joined__gte=last_24h).order_by('-date_joined')
    
    print(f'📊 New users: {recent_users.count()}')
    
    for user in recent_users:
        print(f'\n👤 {user.email}:')
        print(f'   Name: {user.first_name} {user.last_name}')
        print(f'   Type: {user.user_type}')
        print(f'   Registration date: {user.date_joined}')
        print(f'   Referred by: {user.referred_by.email if user.referred_by else "None"}')
        print(f'   Referral code: {user.referral_code}')
        
        # Check subscription
        try:
            subscription = user.subscription
            print(f'   Subscription: {subscription.plan.name} - {subscription.status}')
            
            # Check payments
            payments = Payment.objects.filter(subscription=subscription)
            print(f'   Payments: {payments.count()}')
            
            if payments.exists():
                for payment in payments:
                    print(f'     ${payment.amount} - {payment.status}')
                    
                    # Check commissions
                    commissions = AffiliateCommission.objects.filter(payment=payment)
                    if commissions.exists():
                        for commission in commissions:
                            print(f'       Commission: ${commission.commission_amount} ({commission.status}) → {commission.affiliate.email}')
                    else:
                        print(f'       ❌ No commission')
            else:
                print(f'   ❌ No payments')
                
        except Subscription.DoesNotExist:
            print(f'   ❌ No subscription')

def check_referrer_stats():
    """Check referrers statistics"""
    print('\n📊 Checking referrers statistics:')
    print('=' * 35)
    
    # Find referrers who have referrals
    referrers = User.objects.filter(referrals__isnull=False).distinct()
    
    for referrer in referrers:
        print(f'\n👤 Referrer: {referrer.email}')
        print(f'   Referral code: {referrer.referral_code}')
        
        # Referrals
        referrals = User.objects.filter(referred_by=referrer).order_by('-date_joined')
        print(f'   Total referrals: {referrals.count()}')
        
        for referral in referrals:
            print(f'     {referral.email} - {referral.date_joined.strftime("%Y-%m-%d %H:%M")}')
        
        # Commissions
        commissions = AffiliateCommission.objects.filter(affiliate=referrer)
        total_earned = sum(c.commission_amount for c in commissions)
        pending_amount = sum(c.commission_amount for c in commissions if c.status == 'pending')
        
        print(f'   Commissions: {commissions.count()} (${total_earned} total, ${pending_amount} pending)')

def create_missing_payments_for_new_users():
    """Create missing payments for new users"""
    print('\n🔧 Creating missing payments for new users:')
    print('=' * 55)
    
    # Find active/trialing subscriptions without payments
    subscriptions_without_payments = Subscription.objects.filter(
        status__in=['active', 'trialing']
    ).exclude(
        payments__isnull=False
    )
    
    print(f'📊 Subscriptions without payments: {subscriptions_without_payments.count()}')
    
    created_count = 0
    
    for subscription in subscriptions_without_payments:
        try:
            from django.db import transaction
            from decimal import Decimal
            
            with transaction.atomic():
                # Create payment record
                payment = Payment.objects.create(
                    subscription=subscription,
                    stripe_payment_intent_id=f'pi_manual_{subscription.id}_{int(timezone.now().timestamp())}',
                    amount=subscription.plan.price,
                    currency='USD',
                    status='succeeded'
                )
                
                print(f'✅ Created payment: {subscription.user.email} - ${payment.amount}')
                created_count += 1
                
                # Create commission if the user was referred
                if subscription.user.referred_by:
                    commission_amount = payment.amount * Decimal('0.30')
                    
                    commission = AffiliateCommission.objects.create(
                        affiliate=subscription.user.referred_by,
                        referred_user=subscription.user,
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
                    stats, created = AffiliateStats.objects.get_or_create(user=subscription.user.referred_by)
                    stats.update_stats()
                    
                    print(f'💰 Created commission: {subscription.user.referred_by.email} - ${commission_amount}')
                
        except Exception as e:
            print(f'❌ Error creating payment for subscription {subscription.id}: {str(e)}')
    
    return created_count

def fix_anonymous_user_display():
    """Fix Anonymous User display issue"""
    print('\n🔧 Fixing Anonymous User display issue:')
    print('=' * 40)
    
    from django.db.models import Q
    
    # Find users without names
    users_without_names = User.objects.filter(
        Q(first_name='') | Q(first_name__isnull=True) |
        Q(last_name='') | Q(last_name__isnull=True)
    )
    
    print(f'📊 Users without names: {users_without_names.count()}')
    
    for user in users_without_names:
        print(f'👤 {user.email}: first_name="{user.first_name}", last_name="{user.last_name}"')
        
        # Fix empty names
        if not user.first_name:
            user.first_name = user.email.split('@')[0].title()
        if not user.last_name:
            user.last_name = 'User'
        
        user.save()
        print(f'✅ Fixed name: {user.first_name} {user.last_name}')

def test_affiliate_dashboard_data():
    """Test affiliate dashboard data"""
    print('\n🧪 Testing affiliate dashboard data:')
    print('=' * 40)
    
    try:
        # Test for all referrers
        referrers = User.objects.filter(referrals__isnull=False).distinct()
        
        for referrer in referrers:
            print(f'\n👤 Referrer: {referrer.email}')
            
            # Stats
            stats, created = AffiliateStats.objects.get_or_create(user=referrer)
            stats.update_stats()
            
            print(f'   Total Earnings: ${stats.total_commission_earned}')
            print(f'   Total Referrals: {stats.total_referrals}')
            
            # Recent referrals
            recent_referrals = referrer.referrals.all()[:5]
            print(f'   Recent referrals:')
            for referral in recent_referrals:
                display_name = f"{referral.first_name} {referral.last_name}".strip()
                if not display_name:
                    display_name = referral.email
                print(f'     {display_name} ({referral.email}) - {referral.date_joined.strftime("%Y-%m-%d")}')
            
    except Exception as e:
        print(f'❌ Error: {str(e)}')

def main():
    """Main function"""
    print('🚀 Check and fix new referrals')
    print('=' * 40)
    
    # Check recent users
    check_recent_users()
    
    # Fix Anonymous User issue
    fix_anonymous_user_display()
    
    # Create missing payments
    created_count = create_missing_payments_for_new_users()
    
    # Check referrers statistics
    check_referrer_stats()
    
    # Test dashboard
    test_affiliate_dashboard_data()
    
    print(f'\n✅ Completed fixes')
    if created_count > 0:
        print(f'✅ Created {created_count} new payments')

if __name__ == '__main__':
    main()
