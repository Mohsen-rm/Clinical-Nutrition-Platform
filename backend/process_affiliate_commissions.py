#!/usr/bin/env python
"""
Automatic commission processing script - 30% affiliate system
Runs automatically or manually to process due commissions
"""
import os
import sys
import django
from datetime import datetime, timedelta
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

class AffiliateCommissionProcessor:
    """Automatic commission processor"""
    
    COMMISSION_RATE = Decimal('0.30')  # 30%
    
    def __init__(self):
        self.processed_count = 0
        self.total_commission_amount = Decimal('0.00')
        self.errors = []
    
    def process_new_payments(self):
        """Process new payments whose commissions haven't been processed"""
        print("🔍 Searching for new payments to process commissions...")
        
        # Find successful payments whose commissions haven't been processed
        new_payments = Payment.objects.filter(
            status='succeeded',
            affiliate_commission__isnull=True,  # Commission not yet processed
            subscription__user__referred_by__isnull=False  # User was referred
        ).select_related(
            'subscription__user__referred_by',
            'subscription__plan'
        )
        
        print(f"📊 Found {new_payments.count()} new payments")
        
        for payment in new_payments:
            try:
                self._process_payment_commission(payment)
            except Exception as e:
                error_msg = f"Error processing payment {payment.id}: {str(e)}"
                self.errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return self.processed_count
    
    def _process_payment_commission(self, payment):
        """Process commission for a single payment"""
        with transaction.atomic():
            subscription = payment.subscription
            referred_user = subscription.user
            affiliate = referred_user.referred_by
            
            if not affiliate:
                return
            
            # Calculate commission (30% of amount)
            commission_amount = payment.amount * self.COMMISSION_RATE
            
            print(f"💰 Processing commission: {affiliate.email}")
            print(f"   Original amount: ${payment.amount}")
            print(f"   Commission (30%): ${commission_amount}")
            
            # Create commission record
            commission = AffiliateCommission.objects.create(
                affiliate=affiliate,
                referred_user=referred_user,
                payment=payment,
                commission_amount=commission_amount,
                commission_percentage=self.COMMISSION_RATE * 100,
                commission_type='subscription',
                status='pending'
            )
            
            # Update payment with commission amount
            payment.affiliate_commission = commission_amount
            payment.save()
            
            # Update affiliate stats
            self._update_affiliate_stats(affiliate)
            
            self.processed_count += 1
            self.total_commission_amount += commission_amount
            
            print(f"✅ Commission created successfully: ID {commission.id}")
    
    def _update_affiliate_stats(self, affiliate):
        """Update affiliate stats"""
        stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
        
        if created:
            print(f"📊 Created new stats for affiliate: {affiliate.email}")
        else:
            print(f"📊 Updated stats for affiliate: {affiliate.email}")
    
    def process_recurring_commissions(self):
        """Process recurring commissions for active subscriptions"""
        print("\n🔄 Processing recurring commissions...")
        
        # Find active subscriptions with affiliates
        active_subscriptions = Subscription.objects.filter(
            status__in=['active', 'trialing'],
            user__referred_by__isnull=False
        ).select_related('user__referred_by', 'plan')
        
        print(f"📊 Found {active_subscriptions.count()} active subscriptions with affiliates")
        
        # Process new payments for these subscriptions
        for subscription in active_subscriptions:
            recent_payments = Payment.objects.filter(
                subscription=subscription,
                status='succeeded',
                affiliate_commission__isnull=True,
                created_at__gte=timezone.now() - timedelta(days=32)  # Last month
            )
            
            for payment in recent_payments:
                try:
                    self._process_payment_commission(payment)
                except Exception as e:
                    error_msg = f"Error processing recurring commission for subscription {subscription.id}: {str(e)}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
    
    def mark_commissions_as_paid(self, affiliate_email=None, commission_ids=None):
        """Mark commissions as paid (manual use)"""
        print("\n💳 Marking commissions as paid...")
        
        query = AffiliateCommission.objects.filter(status='pending')
        
        if affiliate_email:
            query = query.filter(affiliate__email=affiliate_email)
            print(f"🎯 Filter for affiliate: {affiliate_email}")
        
        if commission_ids:
            query = query.filter(id__in=commission_ids)
            print(f"🎯 Filter for commissions: {commission_ids}")
        
        commissions = query.all()
        total_amount = sum(c.commission_amount for c in commissions)
        
        print(f"📊 {len(commissions)} commissions will be marked as paid")
        print(f"💰 Total amount: ${total_amount}")
        
        if len(commissions) > 0:
            confirm = input("Proceed? (y/N): ")
            if confirm.lower() == 'y':
                with transaction.atomic():
                    for commission in commissions:
                        commission.status = 'paid'
                        commission.paid_at = timezone.now()
                        commission.save()
                        
                        # تحديث إحصائيات الشريك
                        self._update_affiliate_stats(commission.affiliate)
                
                print(f"✅ Marked {len(commissions)} commissions as paid")
            else:
                print("❌ Operation cancelled")
    
    def generate_commission_report(self):
        """Generate commission report"""
        print("\n📋 Commission report:")
        print("=" * 50)
        
        # General statistics
        total_commissions = AffiliateCommission.objects.count()
        pending_commissions = AffiliateCommission.objects.filter(status='pending').count()
        paid_commissions = AffiliateCommission.objects.filter(status='paid').count()
        
        total_pending_amount = sum(
            c.commission_amount for c in AffiliateCommission.objects.filter(status='pending')
        )
        total_paid_amount = sum(
            c.commission_amount for c in AffiliateCommission.objects.filter(status='paid')
        )
        
        print(f"📊 Total commissions: {total_commissions}")
        print(f"⏳ Pending commissions: {pending_commissions} (${total_pending_amount})")
        print(f"✅ Paid commissions: {paid_commissions} (${total_paid_amount})")
        
        # Top affiliates
        print("\n🏆 Top affiliates:")
        top_affiliates = AffiliateStats.objects.filter(
            total_commission_earned__gt=0
        ).order_by('-total_commission_earned')[:5]
        
        for i, stats in enumerate(top_affiliates, 1):
            print(f"{i}. {stats.user.email}: ${stats.total_commission_earned} "
                  f"({stats.total_referrals} referrals)")
        
        # Pending commissions by affiliate
        print("\n💰 Pending commissions by affiliate:")
        pending_by_affiliate = {}
        for commission in AffiliateCommission.objects.filter(status='pending'):
            email = commission.affiliate.email
            if email not in pending_by_affiliate:
                pending_by_affiliate[email] = Decimal('0.00')
            pending_by_affiliate[email] += commission.commission_amount
        
        for email, amount in sorted(pending_by_affiliate.items(), key=lambda x: x[1], reverse=True):
            print(f"  {email}: ${amount}")
    
    def print_summary(self):
        """Print process summary"""
        print("\n" + "=" * 50)
        print("📋 Commission processing summary:")
        print(f"✅ Processed: {self.processed_count} commissions")
        print(f"💰 Total commissions: ${self.total_commission_amount}")
        
        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("✅ No errors")

def main():
    """Main function"""
    print("🚀 Starting automatic commission processing")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    processor = AffiliateCommissionProcessor()
    
    # Process new payments
    processor.process_new_payments()
    
    # Process recurring commissions
    processor.process_recurring_commissions()
    
    # Generate report
    processor.generate_commission_report()
    
    # Print summary
    processor.print_summary()
    
    print("\n✅ Commission processing completed")

if __name__ == '__main__':
    # Check CLI args
    if len(sys.argv) > 1:
        command = sys.argv[1]
        processor = AffiliateCommissionProcessor()
        
        if command == 'report':
            processor.generate_commission_report()
        elif command == 'pay':
            if len(sys.argv) > 2:
                affiliate_email = sys.argv[2]
                processor.mark_commissions_as_paid(affiliate_email=affiliate_email)
            else:
                processor.mark_commissions_as_paid()
        else:
            print("Available commands:")
            print("  python process_affiliate_commissions.py - process commissions")
            print("  python process_affiliate_commissions.py report - commission report")
            print("  python process_affiliate_commissions.py pay [email] - mark commissions as paid")
    else:
        main()
