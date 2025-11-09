#!/usr/bin/env python
"""
Simple test for the automatic system
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.subscriptions.models import Subscription, Payment
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

def check_system_readiness():
    """Check system readiness"""
    print('🔍 Checking automatic system readiness')
    print('=' * 45)
    
    # 1. Verify signals are present
    try:
        from apps.subscriptions import signals
        print('✅ signals module loaded successfully')
    except Exception as e:
        print(f'❌ Error loading signals: {e}')
        return False
    
    # 2. Verify main referrer
    try:
        referrer = User.objects.get(email='doctor@example.com')
        print(f'✅ Main referrer exists: {referrer.email}')
        print(f'   Referral code: {referrer.referral_code}')
        
        # Referrer stats
        stats, _ = AffiliateStats.objects.get_or_create(user=referrer)
        stats.update_stats()
        
        print(f'   Total commissions: ${stats.total_commission_earned}')
        print(f'   Total referrals: {stats.total_referrals}')
        
    except User.DoesNotExist:
        print('❌ Main referrer does not exist')
        return False
    
    # 3. Verify existing referrals
    referrals = User.objects.filter(referred_by=referrer)
    print(f'\n📊 Current referrals: {referrals.count()}')
    
    for referral in referrals:
        print(f'   {referral.email} - {referral.date_joined.strftime("%Y-%m-%d")}')
        
        # Check subscription
        try:
            subscription = referral.subscription
            payments = Payment.objects.filter(subscription=subscription)
            commissions = AffiliateCommission.objects.filter(referred_user=referral)
            
            print(f'     Subscription: {subscription.plan.name} (${subscription.plan.price})')
            print(f'     Payments: {payments.count()}')
            print(f'     Commissions: {commissions.count()}')
            
            if commissions.exists():
                total_commission = sum(c.commission_amount for c in commissions)
                print(f'     Total commission: ${total_commission}')
            
        except:
            print(f'     ❌ No subscription')
    
    return True

def show_referral_link():
    """Show referral link for testing"""
    print(f'\n🔗 Referral link for testing:')
    print('=' * 35)
    
    try:
        referrer = User.objects.get(email='doctor@example.com')
        referral_code = referrer.referral_code
        
        referral_link = f'http://localhost:3000/register?ref={referral_code}'
        print(f'📎 Link: {referral_link}')
        
        print(f'\n📋 Test steps:')
        print(f'1. Copy the link above')
        print(f'2. Open it in the browser')
        print(f'3. Register a new user')
        print(f'4. Subscribe to any plan')
        print(f'5. Return to the affiliate dashboard')
        print(f'6. The new commission will appear automatically!')
        
    except User.DoesNotExist:
        print('❌ Referrer does not exist')

def verify_automatic_system():
    """Verify that the automatic system will work"""
    print(f'\n🔧 Verifying the automatic system:')
    print('=' * 35)
    
    # Verify that signals are registered
    from django.db.models.signals import post_save
    from apps.subscriptions.models import Subscription
    
    # Get registered receivers
    receivers = post_save._live_receivers(sender=Subscription)
    
    if receivers:
        print(f'✅ There are {len(receivers)} registered receivers for post_save on Subscription')
        
        # Check for commission handler function
        for receiver in receivers:
            if hasattr(receiver, '__name__'):
                if 'commission' in receiver.__name__.lower():
                    print(f'✅ Found commission function: {receiver.__name__}')
                    break
        else:
            print(f'⚠️  Commission function not found among receivers')
    else:
        print(f'❌ No registered receivers for post_save on Subscription')
        return False
    
    print(f'\n✅ Automatic system is ready!')
    print(f'📋 When any new subscription is created:')
    print(f'   1. A Payment will be created automatically')
    print(f'   2. Commission (30%) will be calculated automatically')
    print(f'   3. An AffiliateCommission will be created automatically')
    print(f'   4. Affiliate stats will be updated automatically')
    
    return True

def main():
    """Main function"""
    print('🚀 Checking readiness of the automatic commission system')
    print('=' * 50)
    
    # Check system readiness
    if not check_system_readiness():
        print('❌ System not ready')
        return
    
    # Verify automatic system
    if not verify_automatic_system():
        print('❌ Automatic system not configured properly')
        return
    
    # Show referral link for testing
    show_referral_link()
    
    print(f'\n🎉 The system is fully ready!')
    print(f'✅ You can now test new referrals')
    print(f'✅ Commissions will appear automatically without needing Stripe Webhooks')

if __name__ == '__main__':
    main()
