#!/usr/bin/env python
"""
Check referred users and commissions
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.subscriptions.models import Payment, Subscription
from apps.affiliates.models import AffiliateCommission

User = get_user_model()

def check_test_users():
    """Check users test1 and test2"""
    print('🔍 Checking referred users:')
    print('=' * 50)
    
    # Find users test1 and test2
    test_users = User.objects.filter(email__in=['test1@test.com', 'test2@test.com'])
    
    if not test_users.exists():
        print('❌ test1@test.com or test2@test.com not found')
        # Find users containing 'test'
        test_like = User.objects.filter(email__icontains='test')
        print(f'📧 Users containing "test": {test_like.count()}')
        for user in test_like:
            print(f'  {user.email}')
        return
    
    for user in test_users:
        print(f'👤 {user.email}:')
        print(f'   Referred by: {user.referred_by.email if user.referred_by else "None"}')
        print(f'   Referral code: {user.referral_code}')
        print(f'   Registration date: {user.date_joined}')
        
        # Check subscriptions
        try:
            subscription = user.subscription
            print(f'   Subscription: {subscription.plan.name} - {subscription.status}')
            print(f'   Stripe ID: {subscription.stripe_subscription_id}')
            
            # Check payments
            payments = Payment.objects.filter(subscription=subscription)
            print(f'   Payments: {payments.count()}')
            for payment in payments:
                print(f'     ${payment.amount} - {payment.status} - Commission: {payment.affiliate_commission}')
                
                # Check related commissions
                commissions = AffiliateCommission.objects.filter(payment=payment)
                print(f'     Related commissions: {commissions.count()}')
                
        except Subscription.DoesNotExist:
            print('   ❌ No subscription')
        
        print()

def check_all_commissions():
    """Check all commissions"""
    print('💰 Checking existing commissions:')
    print('=' * 30)
    
    commissions = AffiliateCommission.objects.all()
    print(f'Total commissions: {commissions.count()}')
    
    if commissions.count() == 0:
        print('❌ No commissions in the system!')
        return
    
    for commission in commissions:
        print(f'  {commission.affiliate.email} ← {commission.referred_user.email}')
        print(f'    Amount: ${commission.commission_amount} ({commission.status})')
        print(f'    Date: {commission.created_at}')
        print()

def check_payments_without_commissions():
    """Check payments without commissions"""
    print('🔍 Checking payments without commissions:')
    print('=' * 40)
    
    # Successful payments for referred users
    payments = Payment.objects.filter(
        status='succeeded',
        subscription__user__referred_by__isnull=False
    )
    
    print(f'Successful payments for referred users: {payments.count()}')
    
    payments_without_commissions = []
    for payment in payments:
        commissions = AffiliateCommission.objects.filter(payment=payment)
        if commissions.count() == 0:
            payments_without_commissions.append(payment)
    
    print(f'Payments without commissions: {len(payments_without_commissions)}')
    
    for payment in payments_without_commissions:
        print(f'  Payment ID: {payment.id}')
        print(f'  Amount: ${payment.amount}')
        print(f'  User: {payment.subscription.user.email}')
        print(f'  Referrer: {payment.subscription.user.referred_by.email}')
        print(f'  Date: {payment.created_at}')
        print()
    
    return payments_without_commissions

def check_referral_code():
    """Check the used referral code"""
    print('🔍 Checking referral code 991350C2:')
    print('=' * 35)
    
    try:
        referrer = User.objects.get(referral_code='991350C2')
        print(f'✅ Code owner: {referrer.email}')
        
        # Users referred with this code
        referred_users = User.objects.filter(referred_by=referrer)
        print(f'Referred users: {referred_users.count()}')
        
        for user in referred_users:
            print(f'  {user.email} - {user.date_joined}')
            
    except User.DoesNotExist:
        print('❌ Referral code does not exist!')

def main():
    """Main function"""
    print('🚀 Check referral system for users test1 and test2')
    print('=' * 60)
    
    check_referral_code()
    print()
    
    check_test_users()
    print()
    
    check_all_commissions()
    print()
    
    payments_without_commissions = check_payments_without_commissions()
    
    if payments_without_commissions:
        print('💡 To fix payments without commissions, run:')
        print('   python fix_commission_processing.py')

if __name__ == '__main__':
    main()
