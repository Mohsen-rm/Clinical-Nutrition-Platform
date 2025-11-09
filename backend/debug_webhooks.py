#!/usr/bin/env python
"""
Stripe Webhooks diagnostic tool
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from apps.subscriptions.models import WebhookEvent, Payment, Subscription
from django.utils import timezone
from datetime import timedelta

def check_webhook_events():
    """Check received webhook events"""
    print("🔍 Checking Stripe Webhook events:")
    print("=" * 50)
    
    # Last 24 hours
    last_24h = timezone.now() - timedelta(hours=24)
    recent_events = WebhookEvent.objects.filter(created_at__gte=last_24h)
    
    print(f"📊 Webhook events in the last 24 hours: {recent_events.count()}")
    
    if recent_events.count() == 0:
        print("⚠️  No webhook events received!")
        print("   Check:")
        print("   1. Webhook settings in Stripe Dashboard")
        print("   2. Webhook URL: /api/subscriptions/webhook/")
        print("   3. STRIPE_WEBHOOK_SECRET in environment variables")
        return
    
    # Aggregate events by type
    event_types = {}
    for event in recent_events:
        event_type = event.event_type
        if event_type not in event_types:
            event_types[event_type] = 0
        event_types[event_type] += 1
    
    print("\n📋 Types of received events:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    
    # Check payment events
    payment_events = recent_events.filter(event_type='invoice.payment_succeeded')
    print(f"\n💳 Successful payment events: {payment_events.count()}")
    
    for event in payment_events[:5]:  # first 5 events
        print(f"  {event.stripe_event_id} - processed: {event.processed}")

def check_recent_payments():
    """Check recent payments"""
    print("\n💳 Checking recent payments:")
    print("=" * 50)
    
    last_7_days = timezone.now() - timedelta(days=7)
    recent_payments = Payment.objects.filter(created_at__gte=last_7_days)
    
    print(f"📊 Payments in the last 7 days: {recent_payments.count()}")
    
    for payment in recent_payments:
        has_commission = hasattr(payment, 'commissions') and payment.commissions.exists()
        commission_status = "✅" if has_commission else "❌"
        
        print(f"  {payment.id}: ${payment.amount} - {payment.status} {commission_status}")
        
        if payment.subscription.user.referred_by:
            print(f"    Referred by: {payment.subscription.user.referred_by.email}")
        else:
            print(f"    Not referred")

def simulate_webhook_processing():
    """Simulate webhook processing for recent payments"""
    print("\n🔄 Simulating Webhook processing:")
    print("=" * 50)
    
    # Find payments without commissions
    payments_without_commissions = Payment.objects.filter(
        status='succeeded',
        subscription__user__referred_by__isnull=False,
        commissions__isnull=True
    )
    
    print(f"📊 Payments needing processing: {payments_without_commissions.count()}")
    
    if payments_without_commissions.count() > 0:
        print("\n💡 To process these payments, run:")
        print("   python fix_commission_processing.py")

def main():
    """Main function"""
    print("🔍 Stripe Webhooks diagnostics")
    print("=" * 50)
    
    check_webhook_events()
    check_recent_payments()
    simulate_webhook_processing()
    
    print("\n📋 Recommendations:")
    print("1. Ensure Webhooks are configured in Stripe Dashboard")
    print("2. Run fix_commission_processing.py to process missing commissions")
    print("3. Check Django logs to ensure webhooks are being processed")

if __name__ == '__main__':
    main()
