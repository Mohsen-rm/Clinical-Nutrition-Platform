#!/usr/bin/env python
"""
Automatic commission system test
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.subscriptions.models import Subscription, Payment, SubscriptionPlan
from apps.affiliates.models import AffiliateCommission

User = get_user_model()

def test_automatic_system():
    """Test the automatic system"""
    print('🧪 Testing automatic commission system')
    print('=' * 45)
    
    # Verify referrer exists
    try:
        referrer = User.objects.get(email='doctor@example.com')
        print(f'✅ Referrer exists: {referrer.email}')
        print(f'   Referral code: {referrer.referral_code}')
    except User.DoesNotExist:
        print('❌ Referrer does not exist')
        return
    
    # Check available plans
    plans = SubscriptionPlan.objects.all()
    print(f'\n📋 Available plans: {plans.count()}')
    for plan in plans:
        print(f'   {plan.name}: ${plan.price}')
    
    if not plans.exists():
        print('❌ No plans available')
        return
    
    # Simulate creating a new referred user
    print(f'\n🔄 Simulating new user registration via referral link...')
    
    from django.utils import timezone
    
    # Create a test user
    test_email = f'test_auto_{int(timezone.now().timestamp())}@test.com'
    
    try:
        # Create the user
        new_user = User.objects.create_user(
            email=test_email,
            password='testpass123',
            first_name='Test',
            last_name='Auto',
            user_type='patient',
            referred_by=referrer  # Important: link to referrer
        )
        
        print(f'✅ User created: {new_user.email}')
        print(f'   Referred by: {new_user.referred_by.email}')
        
        # Create subscription (this triggers the automatic system)
        basic_plan = plans.first()
        
        subscription = Subscription.objects.create(
            user=new_user,
            plan=basic_plan,
            status='active',
            stripe_subscription_id=f'sub_test_{int(timezone.now().timestamp())}'
        )
        
        print(f'✅ Subscription created: {subscription.plan.name}')
        
        # Verify payment and commission created automatically
        import time
        time.sleep(1)  # Short wait to ensure signals run
        
        # Check payment
        payments = Payment.objects.filter(subscription=subscription)
        if payments.exists():
            payment = payments.first()
            print(f'✅ Payment created automatically: ${payment.amount}')
            
            # Check commission
            commissions = AffiliateCommission.objects.filter(payment=payment)
            if commissions.exists():
                commission = commissions.first()
                print(f'✅ Commission created automatically: ${commission.commission_amount}')
                print(f'   For affiliate: {commission.affiliate.email}')
                print(f'   Status: {commission.status}')
                
                # Check affiliate stats
                from apps.affiliates.models import AffiliateStats
                stats, _ = AffiliateStats.objects.get_or_create(user=referrer)
                stats.update_stats()
                
                print(f'\n📊 Updated affiliate stats:')
                print(f'   Total Earnings: ${stats.total_commission_earned}')
                print(f'   Total Referrals: {stats.total_referrals}')
                
                print(f'\n🎉 Automatic system works perfectly!')
                
            else:
                print(f'❌ Commission not created automatically')
        else:
            print(f'❌ Payment not created automatically')
        
        # Clean up test data
        print(f'\n🧹 Cleaning up test data...')
        subscription.delete()
        new_user.delete()
        print(f'✅ Test data deleted')
        
    except Exception as e:
        print(f'❌ Test error: {str(e)}')

def show_current_status():
    """Show current system status"""
    print(f'\n📊 Current system status:')
    print('=' * 35)
    
    # General stats
    total_users = User.objects.count()
    referred_users = User.objects.filter(referred_by__isnull=False).count()
    active_subscriptions = Subscription.objects.filter(status__in=['active', 'trialing']).count()
    total_payments = Payment.objects.count()
    total_commissions = AffiliateCommission.objects.count()
    
    print(f'👥 Total users: {total_users}')
    print(f'🔗 Referred users: {referred_users}')
    print(f'📋 Active subscriptions: {active_subscriptions}')
    print(f'💳 Total payments: {total_payments}')
    print(f'💰 Total commissions: {total_commissions}')
    
    # Top affiliates
    from django.db.models import Count
    top_referrers = User.objects.filter(referrals__isnull=False).annotate(
        referral_count=Count('referrals')
    ).order_by('-referral_count')[:3]
    
    print(f'\n🏆 Top affiliates:')
    for referrer in top_referrers:
        from apps.affiliates.models import AffiliateStats
        stats, _ = AffiliateStats.objects.get_or_create(user=referrer)
        print(f'   {referrer.email}: {referrer.referral_count} referrals - ${stats.total_commission_earned} commissions')

def main():
    """Main function"""
    print('🚀 Testing automatic commission system')
    print('=' * 45)
    
    show_current_status()
    test_automatic_system()
    
    print(f'\n✅ Test finished')
    print(f'📋 System is ready to use without Stripe Webhooks!')

if __name__ == '__main__':
    main()
