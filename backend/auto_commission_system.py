#!/usr/bin/env python

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
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.subscriptions.models import Payment, Subscription
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

def create_payment_and_commission(subscription):
    """Create the payment and commission for the subscription"""
    try:
        with transaction.atomic():
            # Check for an existing payment
            existing_payment = Payment.objects.filter(subscription=subscription).first()
            if existing_payment:
                print(f'⚠️  Payment already exists for subscription {subscription.id}')
                return existing_payment
            
            # Create payment record
            payment = Payment.objects.create(
                subscription=subscription,
                stripe_payment_intent_id=f'pi_auto_{subscription.id}_{int(timezone.now().timestamp())}',
                amount=subscription.plan.price,
                currency='USD',
                status='succeeded'
            )
            
            print(f'✅ Created automatic payment: {subscription.user.email} - ${payment.amount}')
            
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
                
                print(f'💰 Created automatic commission: {subscription.user.referred_by.email} - ${commission_amount}')
            
            return payment
            
    except Exception as e:
        print(f'❌ Error creating automatic payment: {str(e)}')
        return None

def process_all_subscriptions_without_payments():
    """Process all subscriptions without payments"""
    print('🔄 Processing all subscriptions without payments:')
    print('=' * 50)
    
    # Find all active or trialing subscriptions without payments
    subscriptions_without_payments = Subscription.objects.filter(
        status__in=['active', 'trialing']
    ).exclude(
        payments__isnull=False
    )
    
    print(f'📊 Subscriptions needing processing: {subscriptions_without_payments.count()}')
    
    processed_count = 0
    total_commissions = Decimal('0.00')
    
    for subscription in subscriptions_without_payments:
        payment = create_payment_and_commission(subscription)
        if payment:
            processed_count += 1
            if payment.affiliate_commission:
                total_commissions += payment.affiliate_commission
    
    print(f'\n📋 Results:')
    print(f'✅ Processed {processed_count} subscriptions')
    print(f'💰 Total commissions created: ${total_commissions}')
    
    return processed_count

def setup_automatic_commission_system():
    """Set up the automatic commissions system"""
    print('\n🔧 Setting up the automatic commissions system:')
    print('=' * 40)
    
    # Create signals file for automatic processing
    signals_content = '''
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.subscriptions.models import Subscription, Payment
from apps.affiliates.models import AffiliateCommission, AffiliateStats
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

@receiver(post_save, sender=Subscription)
def create_payment_and_commission_on_subscription(sender, instance, created, **kwargs):
    """Automatically create payment and commission when a new subscription is created"""
    if created and instance.status in ['active', 'trialing']:
        # Ensure there is no existing payment
        existing_payment = Payment.objects.filter(subscription=instance).first()
        if existing_payment:
            return
        
        try:
            with transaction.atomic():
                # Create payment
                payment = Payment.objects.create(
                    subscription=instance,
                    stripe_payment_intent_id=f'pi_auto_{instance.id}_{int(timezone.now().timestamp())}',
                    amount=instance.plan.price,
                    currency='USD',
                    status='succeeded'
                )
                
                # Create commission if the user was referred
                if instance.user.referred_by:
                    commission_amount = payment.amount * Decimal('0.30')
                    
                    AffiliateCommission.objects.create(
                        affiliate=instance.user.referred_by,
                        referred_user=instance.user,
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
                    stats, created = AffiliateStats.objects.get_or_create(user=instance.user.referred_by)
                    stats.update_stats()
                    
        except Exception as e:
            print(f'Error creating automatic commission: {str(e)}')
'''
    
    # Write signals file
    signals_file_path = '/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend/apps/subscriptions/signals.py'
    
    try:
        with open(signals_file_path, 'w', encoding='utf-8') as f:
            f.write(signals_content)
        print(f'✅ Created signals file: {signals_file_path}')
    except Exception as e:
        print(f'❌ Error creating signals file: {str(e)}')
    
    # Update __init__.py to load signals
    init_file_path = '/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend/apps/subscriptions/__init__.py'
    
    try:
        init_content = '''
default_app_config = 'apps.subscriptions.apps.SubscriptionsConfig'
'''
        with open(init_file_path, 'w', encoding='utf-8') as f:
            f.write(init_content)
        print(f'✅ Updated __init__.py')
    except Exception as e:
        print(f'❌ Error updating __init__.py: {str(e)}')
    
    # Update apps.py to load signals
    apps_file_path = '/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend/apps/subscriptions/apps.py'
    
    apps_content = '''
from django.apps import AppConfig

class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.subscriptions'
    
    def ready(self):
        import apps.subscriptions.signals
'''
    
    try:
        with open(apps_file_path, 'w', encoding='utf-8') as f:
            f.write(apps_content)
        print(f'✅ Updated apps.py to load signals')
    except Exception as e:
        print(f'❌ Error updating apps.py: {str(e)}')

def verify_system_status():
    """Verify system status"""
    print('\n📊 Verifying system status:')
    print('=' * 30)
    
    # General stats
    total_subscriptions = Subscription.objects.filter(status__in=['active', 'trialing']).count()
    subscriptions_with_payments = Subscription.objects.filter(
        status__in=['active', 'trialing'],
        payments__isnull=False
    ).distinct().count()
    
    print(f'📋 Total active subscriptions: {total_subscriptions}')
    print(f'💳 Subscriptions with payments: {subscriptions_with_payments}')
    print(f'❌ Subscriptions without payments: {total_subscriptions - subscriptions_with_payments}')
    
    # Commission stats
    total_commissions = AffiliateCommission.objects.count()
    pending_commissions = AffiliateCommission.objects.filter(status='pending').count()
    total_commission_amount = sum(c.commission_amount for c in AffiliateCommission.objects.all())
    
    print(f'\n💰 Commission stats:')
    print(f'   Total commissions: {total_commissions}')
    print(f'   Pending commissions: {pending_commissions}')
    print(f'   Total amount: ${total_commission_amount}')
    
    # Top referrers
    from django.db.models import Count
    top_referrers = User.objects.filter(referrals__isnull=False).annotate(
        referral_count=Count('referrals')
    ).order_by('-referral_count')[:3]
    
    print(f'\n🏆 Top referrers:')
    for referrer in top_referrers:
        stats, _ = AffiliateStats.objects.get_or_create(user=referrer)
        print(f'   {referrer.email}: {referrer.referral_count} referrals - ${stats.total_commission_earned} commissions')

def main():
    """Main function"""
    print('🚀 Automatic commissions system - final solution')
    print('=' * 50)
    
    # Process current subscriptions
    processed_count = process_all_subscriptions_without_payments()
    
    # Set up the automatic system
    setup_automatic_commission_system()
    
    # Verify system status
    verify_system_status()
    
    print(f'\n✅ Finished setting up the automatic system')
    print(f'📋 Now all new subscriptions will automatically create payments and commissions')
    
    if processed_count > 0:
        print(f'✅ Processed {processed_count} existing subscriptions')
    
    print(f'\n🔄 To apply changes, restart the server:')
    print(f'   cd backend && python manage.py runserver')

if __name__ == '__main__':
    main()
