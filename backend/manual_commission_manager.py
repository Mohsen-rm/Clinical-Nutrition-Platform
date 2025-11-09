#!/usr/bin/env python
"""
Manual Commission Manager - Tools to manage commissions and payments
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
from apps.affiliates.models import AffiliateCommission, AffiliateStats, PayoutRequest

User = get_user_model()

class ManualCommissionManager:
    """Manual Commission Manager"""
    
    def __init__(self):
        self.COMMISSION_RATE = Decimal('0.30')  # 30%
    
    def show_main_menu(self):
        """Show main menu"""
        while True:
            print("\n" + "=" * 60)
            print("🏥 Manual Commission Manager - Clinical Nutrition Platform")
            print("=" * 60)
            print("1. 📊 Show commissions report")
            print("2. 👥 Show affiliates and stats")
            print("3. 💰 Show pending commissions")
            print("4. ✅ Mark commissions as paid")
            print("5. 🔍 Search affiliate")
            print("6. 📋 Show payout requests")
            print("7. ➕ Create manual commission")
            print("8. 🔄 Update affiliates' stats")
            print("9. 📈 Detailed affiliate report")
            print("0. 🚪 Exit")
            print("-" * 60)
            
            choice = input("Choose an option number: ").strip()
            
            if choice == '1':
                self.show_commission_report()
            elif choice == '2':
                self.show_affiliates_list()
            elif choice == '3':
                self.show_pending_commissions()
            elif choice == '4':
                self.mark_commissions_paid()
            elif choice == '5':
                self.search_affiliate()
            elif choice == '6':
                self.show_payout_requests()
            elif choice == '7':
                self.create_manual_commission()
            elif choice == '8':
                self.update_all_stats()
            elif choice == '9':
                self.detailed_affiliate_report()
            elif choice == '0':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice, try again")
    
    def show_commission_report(self):
        """Show comprehensive commissions report"""
        print("\n📋 Comprehensive commissions report")
        print("=" * 50)
        
        # General statistics
        total_commissions = AffiliateCommission.objects.count()
        pending_commissions = AffiliateCommission.objects.filter(status='pending')
        paid_commissions = AffiliateCommission.objects.filter(status='paid')
        
        total_pending_amount = sum(c.commission_amount for c in pending_commissions)
        total_paid_amount = sum(c.commission_amount for c in paid_commissions)
        
        print(f"📊 Total commissions: {total_commissions}")
        print(f"⏳ Pending commissions: {pending_commissions.count()} (${total_pending_amount:.2f})")
        print(f"✅ Paid commissions: {paid_commissions.count()} (${total_paid_amount:.2f})")
        print(f"💰 Total commission amount: ${total_pending_amount + total_paid_amount:.2f}")
        
        # Commissions by month
        print("\n📅 Commissions by month (last 6 months):")
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_commissions = AffiliateCommission.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            )
            month_amount = sum(c.commission_amount for c in month_commissions)
            
            print(f"  {month_start.strftime('%Y-%m')}: {month_commissions.count()} commissions (${month_amount:.2f})")
        
        # Top affiliates
        print("\n🏆 Top 10 affiliates:")
        top_affiliates = AffiliateStats.objects.filter(
            total_commission_earned__gt=0
        ).order_by('-total_commission_earned')[:10]
        
        for i, stats in enumerate(top_affiliates, 1):
            available = stats.total_commission_earned - stats.total_commission_paid
            print(f"{i:2d}. {stats.user.email:<30} "
                  f"Total: ${stats.total_commission_earned:>8.2f} "
                  f"Available: ${available:>8.2f} "
                  f"Referrals: {stats.total_referrals:>3d}")
    
    def show_affiliates_list(self):
        """Show affiliates list"""
        print("\n👥 Affiliates list")
        print("=" * 80)
        
        affiliates = User.objects.filter(
            affiliate_commissions__isnull=False
        ).distinct().order_by('email')
        
        if not affiliates:
            print("❌ No affiliates currently")
            return
        
        print(f"{'#':<3} {'Email':<30} {'Referrals':<8} {'Commissions':<10} {'Paid':<10} {'Pending':<10}")
        print("-" * 80)
        
        for i, affiliate in enumerate(affiliates, 1):
            stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
            pending = stats.total_commission_earned - stats.total_commission_paid
            
            print(f"{i:<3} {affiliate.email:<30} "
                  f"{stats.total_referrals:<8} "
                  f"${stats.total_commission_earned:<9.2f} "
                  f"${stats.total_commission_paid:<9.2f} "
                  f"${pending:<9.2f}")
    
    def show_pending_commissions(self):
        """Show pending commissions"""
        print("\n💰 Pending commissions")
        print("=" * 100)
        
        pending_commissions = AffiliateCommission.objects.filter(
            status='pending'
        ).order_by('-created_at')
        
        if not pending_commissions:
            print("✅ No pending commissions")
            return
        
        print(f"{'ID':<5} {'Affiliate':<25} {'Amount':<10} {'Type':<12} {'Date':<12} {'Referred':<25}")
        print("-" * 100)
        
        total_pending = Decimal('0.00')
        for commission in pending_commissions:
            total_pending += commission.commission_amount
            print(f"{commission.id:<5} "
                  f"{commission.affiliate.email:<25} "
                  f"${commission.commission_amount:<9.2f} "
                  f"{commission.commission_type:<12} "
                  f"{commission.created_at.strftime('%Y-%m-%d'):<12} "
                  f"{commission.referred_user.email:<25}")
        
        print("-" * 100)
        print(f"Total pending commissions: ${total_pending:.2f}")
    
    def mark_commissions_paid(self):
        """Mark commissions as paid"""
        print("\n✅ Mark commissions as paid")
        print("=" * 50)
        
        print("Choose method:")
        print("1. Mark all pending commissions")
        print("2. Mark a specific affiliate's commissions")
        print("3. Mark specific commissions by ID")
        print("4. Back to main menu")
        
        choice = input("Choose an option number: ").strip()
        
        if choice == '1':
            self._mark_all_pending_paid()
        elif choice == '2':
            self._mark_affiliate_commissions_paid()
        elif choice == '3':
            self._mark_specific_commissions_paid()
        elif choice == '4':
            return
        else:
            print("❌ Invalid choice")
    
    def _mark_all_pending_paid(self):
        """Mark all pending commissions as paid"""
        pending_commissions = AffiliateCommission.objects.filter(status='pending')
        total_amount = sum(c.commission_amount for c in pending_commissions)
        
        print(f"📊 {pending_commissions.count()} commissions will be marked as paid")
        print(f"💰 Total amount: ${total_amount:.2f}")
        
        if pending_commissions.count() == 0:
            print("❌ No pending commissions")
            return
        
        confirm = input("Proceed? (y/N): ")
        if confirm.lower() == 'y':
            with transaction.atomic():
                for commission in pending_commissions:
                    commission.status = 'paid'
                    commission.paid_at = timezone.now()
                    commission.save()
                
                # Update stats for all affiliates
                affiliates = set(c.affiliate for c in pending_commissions)
                for affiliate in affiliates:
                    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
                    stats.update_stats()
            
            print(f"✅ Marked {pending_commissions.count()} commissions as paid")
        else:
            print("❌ Operation cancelled")
    
    def _mark_affiliate_commissions_paid(self):
        """Mark commissions for a specific affiliate as paid"""
        email = input("Enter affiliate email: ").strip()
        
        try:
            affiliate = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"❌ User not found: {email}")
            return
        
        pending_commissions = AffiliateCommission.objects.filter(
            affiliate=affiliate,
            status='pending'
        )
        
        if not pending_commissions:
            print(f"❌ No pending commissions for affiliate: {email}")
            return
        
        total_amount = sum(c.commission_amount for c in pending_commissions)
        
        print(f"📊 {pending_commissions.count()} commissions will be marked as paid for affiliate: {email}")
        print(f"💰 Total amount: ${total_amount:.2f}")
        
        # Show commission details
        print("\nCommission details:")
        for commission in pending_commissions:
            print(f"  ID: {commission.id} - ${commission.commission_amount:.2f} - {commission.created_at.strftime('%Y-%m-%d')}")
        
        confirm = input("Proceed? (y/N): ")
        if confirm.lower() == 'y':
            with transaction.atomic():
                for commission in pending_commissions:
                    commission.status = 'paid'
                    commission.paid_at = timezone.now()
                    commission.save()
                
                # Update affiliate stats
                stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
                stats.update_stats()
            
            print(f"✅ Marked {pending_commissions.count()} commissions as paid for affiliate: {email}")
        else:
            print("❌ Operation cancelled")
    
    def _mark_specific_commissions_paid(self):
        """Mark specific commissions by ID as paid"""
        ids_input = input("Enter commission IDs separated by commas (e.g., 1,2,3): ").strip()
        
        try:
            commission_ids = [int(id.strip()) for id in ids_input.split(',')]
        except ValueError:
            print("❌ Invalid number format")
            return
        
        commissions = AffiliateCommission.objects.filter(
            id__in=commission_ids,
            status='pending'
        )
        
        if not commissions:
            print("❌ No pending commissions found for these IDs")
            return
        
        total_amount = sum(c.commission_amount for c in commissions)
        
        print(f"📊 {commissions.count()} commissions will be marked as paid")
        print(f"💰 Total amount: ${total_amount:.2f}")
        
        # Show commission details
        print("\nCommission details:")
        for commission in commissions:
            print(f"  ID: {commission.id} - {commission.affiliate.email} - ${commission.commission_amount:.2f}")
        
        confirm = input("Proceed? (y/N): ")
        if confirm.lower() == 'y':
            with transaction.atomic():
                for commission in commissions:
                    commission.status = 'paid'
                    commission.paid_at = timezone.now()
                    commission.save()
                
                # Update affiliates' stats
                affiliates = set(c.affiliate for c in commissions)
                for affiliate in affiliates:
                    stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
                    stats.update_stats()
            
            print(f"✅ Marked {commissions.count()} commissions as paid")
        else:
            print("❌ Operation cancelled")
    
    def search_affiliate(self):
        """Search for a specific affiliate"""
        email = input("Enter affiliate email: ").strip()
        
        try:
            affiliate = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"❌ User not found: {email}")
            return
        
        print(f"\n🔍 Affiliate details: {email}")
        print("=" * 60)
        
        # Stats
        stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
        
        print(f"📊 Total referrals: {stats.total_referrals}")
        print(f"🟢 Active referrals: {stats.active_referrals}")
        print(f"💰 Total commissions: ${stats.total_commission_earned:.2f}")
        print(f"✅ Paid commissions: ${stats.total_commission_paid:.2f}")
        print(f"⏳ Pending commissions: ${stats.total_commission_pending:.2f}")
        
        # Recent commissions
        recent_commissions = AffiliateCommission.objects.filter(
            affiliate=affiliate
        ).order_by('-created_at')[:10]
        
        if recent_commissions:
            print(f"\n📋 Last {len(recent_commissions)} commissions:")
            print(f"{'ID':<5} {'Amount':<10} {'Status':<10} {'Date':<12} {'Referred':<25}")
            print("-" * 70)
            
            for commission in recent_commissions:
                print(f"{commission.id:<5} "
                      f"${commission.commission_amount:<9.2f} "
                      f"{commission.status:<10} "
                      f"{commission.created_at.strftime('%Y-%m-%d'):<12} "
                      f"{commission.referred_user.email:<25}")
    
    def show_payout_requests(self):
        """Show payout requests"""
        print("\n📋 Payout requests")
        print("=" * 80)
        
        payout_requests = PayoutRequest.objects.all().order_by('-created_at')
        
        if not payout_requests:
            print("❌ No payout requests")
            return
        
        print(f"{'ID':<5} {'Affiliate':<25} {'Amount':<10} {'Status':<12} {'Date':<12} {'Method':<15}")
        print("-" * 80)
        
        for request in payout_requests:
            print(f"{request.id:<5} "
                  f"{request.affiliate.email:<25} "
                  f"${request.amount:<9.2f} "
                  f"{request.status:<12} "
                  f"{request.created_at.strftime('%Y-%m-%d'):<12} "
                  f"{request.payment_method:<15}")
    
    def create_manual_commission(self):
        """Create a manual commission"""
        print("\n➕ Create a manual commission")
        print("=" * 50)
        
        # Select affiliate
        affiliate_email = input("Affiliate email: ").strip()
        try:
            affiliate = User.objects.get(email=affiliate_email)
        except User.DoesNotExist:
            print(f"❌ User not found: {affiliate_email}")
            return
        
        # Select referred user
        referred_email = input("Referred user email: ").strip()
        try:
            referred_user = User.objects.get(email=referred_email)
        except User.DoesNotExist:
            print(f"❌ User not found: {referred_email}")
            return
        
        # Amount
        try:
            amount = Decimal(input("Commission amount: $").strip())
        except:
            print("❌ Invalid amount")
            return
        
        # Notes
        notes = input("Notes (optional): ").strip()
        
        print(f"\n📋 Confirm commission creation:")
        print(f"Affiliate: {affiliate_email}")
        print(f"Referred: {referred_email}")
        print(f"Amount: ${amount:.2f}")
        print(f"Notes: {notes or 'None'}")
        
        confirm = input("Create commission? (y/N): ")
        if confirm.lower() == 'y':
            commission = AffiliateCommission.objects.create(
                affiliate=affiliate,
                referred_user=referred_user,
                payment=None,  # Manual commission
                commission_amount=amount,
                commission_percentage=self.COMMISSION_RATE * 100,
                commission_type='one_time',
                status='pending',
                notes=notes
            )
            
            # Update affiliate stats
            stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
            stats.update_stats()
            
            print(f"✅ Commission created successfully: ID {commission.id}")
        else:
            print("❌ Operation cancelled")
    
    def update_all_stats(self):
        """Update all affiliates' stats"""
        print("\n🔄 Updating affiliates' stats...")
        
        affiliates = User.objects.filter(
            affiliate_commissions__isnull=False
        ).distinct()
        
        updated_count = 0
        for affiliate in affiliates:
            stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
            stats.update_stats()
            updated_count += 1
            
            if created:
                print(f"➕ Created new stats: {affiliate.email}")
            else:
                print(f"🔄 Updated stats: {affiliate.email}")
        
        print(f"✅ Updated stats for {updated_count} affiliates")
    
    def detailed_affiliate_report(self):
        """Detailed report for an affiliate"""
        email = input("Enter affiliate email: ").strip()
        
        try:
            affiliate = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"❌ User not found: {email}")
            return
        
        print(f"\n📈 Detailed affiliate report: {email}")
        print("=" * 80)
        
        # General stats
        stats, _ = AffiliateStats.objects.get_or_create(user=affiliate)
        stats.update_stats()
        
        print(f"📊 General stats:")
        print(f"  Total referrals: {stats.total_referrals}")
        print(f"  Active referrals: {stats.active_referrals}")
        print(f"  Total commissions: ${stats.total_commission_earned:.2f}")
        print(f"  Paid commissions: ${stats.total_commission_paid:.2f}")
        print(f"  Pending commissions: ${stats.total_commission_pending:.2f}")
        
        # Referrals
        referrals = User.objects.filter(referred_by=affiliate)
        if referrals:
            print(f"\n👥 Referrals ({referrals.count()}):")
            for referral in referrals:
                subscription_status = "Not subscribed"
                if hasattr(referral, 'subscription'):
                    subscription_status = referral.subscription.status
                
                print(f"  {referral.email} - {subscription_status}")
        
        # Commissions by month
        print(f"\n📅 Commissions by month (last 12 months):")
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_commissions = AffiliateCommission.objects.filter(
                affiliate=affiliate,
                created_at__gte=month_start,
                created_at__lte=month_end
            )
            month_amount = sum(c.commission_amount for c in month_commissions)
            
            if month_commissions.count() > 0:
                print(f"  {month_start.strftime('%Y-%m')}: {month_commissions.count()} commissions (${month_amount:.2f})")

def main():
    """Main function"""
    manager = ManualCommissionManager()
    manager.show_main_menu()

if __name__ == '__main__':
    main()
