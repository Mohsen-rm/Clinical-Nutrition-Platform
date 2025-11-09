#!/usr/bin/env python
"""
Create sample commission data to test the system
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
from apps.subscriptions.models import Payment, Subscription, SubscriptionPlan
from apps.affiliates.models import AffiliateCommission, AffiliateStats

User = get_user_model()

def create_test_commissions():
    """Create test commissions"""
    print("🚀 Creating sample commission data...")
    
    try:
        # Get users
        admin = User.objects.get(email='admin@example.com')
        doctor = User.objects.get(email='doctor@example.com')
        patient = User.objects.get(email='patient@example.com')
        
        # Get a subscription plan
        basic_plan = SubscriptionPlan.objects.filter(name__icontains='basic').first()
        if not basic_plan:
            print("❌ Basic plan not found")
            return
        
        print(f"📋 Using plan: {basic_plan.name} - ${basic_plan.price}")
        
        # Create sample subscriptions if missing
        subscription1, created = Subscription.objects.get_or_create(
            user=patient,
            defaults={
                'plan': basic_plan,
                'stripe_subscription_id': 'sub_test_001',
                'status': 'active',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timezone.timedelta(days=30),
            }
        )
        
        if created:
            print(f"✅ Created new subscription for patient")
        
        # Create sample payments
        payments_data = [
            {
                'subscription': subscription1,
                'amount': Decimal('29.00'),
                'stripe_payment_intent_id': 'pi_test_001',
                'status': 'succeeded',
                'affiliate_commission': None,  # Commission not processed yet
            },
            {
                'subscription': subscription1,
                'amount': Decimal('29.00'),
                'stripe_payment_intent_id': 'pi_test_002',
                'status': 'succeeded',
                'affiliate_commission': None,
            },
        ]
        
        created_payments = []
        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(
                stripe_payment_intent_id=payment_data['stripe_payment_intent_id'],
                defaults=payment_data
            )
            if created:
                created_payments.append(payment)
                print(f"✅ Created payment: {payment.stripe_payment_intent_id} - ${payment.amount}")
        
        # Set patient as referred by admin
        if not patient.referred_by:
            patient.referred_by = admin
            patient.save()
            print(f"✅ Set {patient.email} as referred by {admin.email}")
        
        # Manually create sample commissions
        commission_data = [
            {
                'affiliate': admin,
                'referred_user': patient,
                'payment': created_payments[0] if created_payments else None,
                'commission_amount': Decimal('8.70'),  # 30% of $29
                'commission_percentage': Decimal('30.00'),
                'commission_type': 'subscription',
                'status': 'pending',
                'notes': 'Sample commission - monthly subscription'
            },
            {
                'affiliate': admin,
                'referred_user': patient,
                'payment': created_payments[1] if len(created_payments) > 1 else None,
                'commission_amount': Decimal('8.70'),  # 30% of $29
                'commission_percentage': Decimal('30.00'),
                'commission_type': 'subscription',
                'status': 'pending',
                'notes': 'Sample commission - monthly renewal'
            },
            {
                'affiliate': doctor,
                'referred_user': patient,
                'payment': None,  # Manual commission
                'commission_amount': Decimal('15.00'),
                'commission_percentage': Decimal('30.00'),
                'commission_type': 'one_time',
                'status': 'paid',
                'paid_at': timezone.now(),
                'notes': 'Manual commission - special bonus'
            },
        ]
        
        created_commissions = []
        for comm_data in commission_data:
            # Ensure commission does not already exist
            existing = AffiliateCommission.objects.filter(
                affiliate=comm_data['affiliate'],
                referred_user=comm_data['referred_user'],
                commission_amount=comm_data['commission_amount'],
                commission_type=comm_data['commission_type']
            ).first()
            
            if not existing:
                commission = AffiliateCommission.objects.create(**comm_data)
                created_commissions.append(commission)
                print(f"✅ Created commission: {commission.affiliate.email} - ${commission.commission_amount} ({commission.status})")
        
        # Update affiliate stats
        for affiliate in [admin, doctor]:
            stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
            stats.update_stats()
            if created:
                print(f"✅ Created new stats: {affiliate.email}")
            else:
                print(f"🔄 Updated stats: {affiliate.email}")
        
        print(f"\n📊 Summary of created data:")
        print(f"💳 Payments: {len(created_payments)}")
        print(f"💰 Commissions: {len(created_commissions)}")
        
        # Show stats
        print(f"\n📈 Affiliate stats:")
        for affiliate in [admin, doctor]:
            stats = AffiliateStats.objects.get(user=affiliate)
            print(f"{affiliate.email}:")
            print(f"  Total commissions: ${stats.total_commission_earned}")
            print(f"  Paid commissions: ${stats.total_commission_paid}")
            print(f"  Pending commissions: ${stats.total_commission_pending}")
            print(f"  Total referrals: {stats.total_referrals}")
        
        print("\n✅ All sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_commissions()
