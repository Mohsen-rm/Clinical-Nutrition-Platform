#!/usr/bin/env python
"""
Manually create missing payment and commission records
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
from django.db import transaction
from django.utils import timezone
from apps.subscriptions.models import Payment, Subscription
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

def create_missing_payments():
    """Create missing payment records for active subscriptions"""
    print('🔧 Creating missing payment records:')
    print('=' * 50)
    
    # Find active/trialing subscriptions without payments
    subscriptions_without_payments = Subscription.objects.filter(
        status__in=['active', 'trialing']
    ).exclude(
        payments__isnull=False
    )
    
    print(f'📊 Subscriptions without payments: {subscriptions_without_payments.count()}')
    
    created_payments = []
    
    for subscription in subscriptions_without_payments:
        try:
            with transaction.atomic():
                # Create payment record based on plan price
                payment = Payment.objects.create(
                    subscription=subscription,
                    stripe_payment_intent_id=f'pi_manual_{subscription.id}_{int(timezone.now().timestamp())}',
                    amount=subscription.plan.price,
                    currency='USD',
                    status='succeeded'
                )
                
                created_payments.append(payment)
                
                print(f'✅ Created payment: {subscription.user.email} - ${payment.amount}')
                
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
    
    return created_payments

def verify_test_users():
    """Verify specifically users test1 and test2"""
    print('\n🔍 Verifying users test1 and test2:')
    print('=' * 45)
    
    test_users = ['test1@test.com', 'test2@test.com']
    
    for email in test_users:
        try:
            user = User.objects.get(email=email)
            print(f'\n👤 {email}:')
            print(f'   Referred by: {user.referred_by.email if user.referred_by else "None"}')
            
            try:
                subscription = user.subscription
                print(f'   Subscription: {subscription.plan.name} (${subscription.plan.price})')
                print(f'   Subscription status: {subscription.status}')
                
                payments = Payment.objects.filter(subscription=subscription)
                print(f'   Payments: {payments.count()}')
                
                if payments.exists():
                    for payment in payments:
                        print(f'     ${payment.amount} - {payment.status}')
                        
                        commissions = AffiliateCommission.objects.filter(payment=payment)
                        if commissions.exists():
                            for commission in commissions:
                                print(f'       Commission: ${commission.commission_amount} ({commission.status})')
                        else:
                            print(f'       ❌ No commission')
                else:
                    print(f'   ❌ No payments found')
                    
            except Subscription.DoesNotExist:
                print(f'   ❌ No subscription')
                
        except User.DoesNotExist:
            print(f'❌ User {email} does not exist')

def check_referrer_dashboard():
    """Check referrer dashboard"""
    print('\n📊 Checking referrer dashboard (doctor@example.com):')
    print('=' * 50)
    
    try:
        referrer = User.objects.get(email='doctor@example.com')
        
        # Referrals
        referrals = User.objects.filter(referred_by=referrer)
        print(f'Total referrals: {referrals.count()}')
        
        for referral in referrals:
            print(f'  {referral.email} - {referral.date_joined.strftime("%Y-%m-%d")}')
        
        # Commissions
        commissions = AffiliateCommission.objects.filter(affiliate=referrer)
        total_earned = sum(c.commission_amount for c in commissions)
        pending_amount = sum(c.commission_amount for c in commissions if c.status == 'pending')
        
        print(f'\nCommissions:')
        print(f'  Total commissions: {commissions.count()}')
        print(f'  Total amount: ${total_earned}')
        print(f'  Pending amount: ${pending_amount}')
        
        # Stats
        try:
            stats = AffiliateStats.objects.get(user=referrer)
            stats.update_stats()
            print(f'\nStats:')
            print(f'  Total Earnings: ${stats.total_commission_earned}')
            print(f'  Pending: ${stats.total_commission_pending}')
            print(f'  Paid: ${stats.total_commission_paid}')
        except AffiliateStats.DoesNotExist:
            print(f'\n❌ No stats found')
            
    except User.DoesNotExist:
        print('❌ Referrer does not exist')

def main():
    """Main function"""
    print('🚀 Fix payments and commissions for users test1 and test2')
    print('=' * 65)
    
    # Verify current state
    verify_test_users()
    
    # Create missing payments
    created_payments = create_missing_payments()
    
    if created_payments:
        print(f'\n✅ Created {len(created_payments)} new payments')
        
        # Verify again
        verify_test_users()
        
        # Check referrer dashboard
        check_referrer_dashboard()
    else:
        print('\n✅ All payments exist')

if __name__ == '__main__':
    main()
