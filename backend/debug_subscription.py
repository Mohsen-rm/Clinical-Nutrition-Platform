#!/usr/bin/env python
"""
Debug script to test subscription creation and see what Stripe returns
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

import stripe
from django.conf import settings
from apps.subscriptions.models import SubscriptionPlan
from django.contrib.auth import get_user_model

User = get_user_model()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def debug_subscription_creation():
    """Debug what happens during subscription creation"""
    
    print("🔍 Debugging subscription creation...")
    
    try:
        # Get Basic Plan
        plan = SubscriptionPlan.objects.get(plan_type='basic')
        print(f"✅ Plan found: {plan.name} - {plan.stripe_price_id}")
        
        # Create test customer
        customer = stripe.Customer.create(
            email='debug@example.com',
            name='Debug User'
        )
        print(f"✅ Customer created: {customer.id}")
        
        # Create test payment method
        payment_method = stripe.PaymentMethod.create(
            type='card',
            card={
                'number': '4242424242424242',
                'exp_month': 12,
                'exp_year': 2025,
                'cvc': '123',
            },
        )
        print(f"✅ Payment method created: {payment_method.id}")
        
        # Attach payment method
        stripe.PaymentMethod.attach(
            payment_method.id,
            customer=customer.id,
        )
        print(f"✅ Payment method attached")
        
        # Create subscription and inspect the response
        print("\n🔍 Creating subscription...")
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{
                'price': plan.stripe_price_id,
            }],
            default_payment_method=payment_method.id,
            expand=['latest_invoice.payment_intent'],
        )
        
        print(f"✅ Subscription created: {subscription.id}")
        print(f"📋 Subscription details:")
        print(f"   Status: {subscription.status}")
        print(f"   Current period start: {subscription.current_period_start}")
        print(f"   Current period end: {subscription.current_period_end}")
        print(f"   Type of current_period_start: {type(subscription.current_period_start)}")
        
        if subscription.current_period_start:
            from django.utils import timezone
            start_datetime = timezone.datetime.fromtimestamp(
                subscription.current_period_start, tz=timezone.utc
            )
            end_datetime = timezone.datetime.fromtimestamp(
                subscription.current_period_end, tz=timezone.utc
            )
            print(f"   Converted start: {start_datetime}")
            print(f"   Converted end: {end_datetime}")
        else:
            print("   ❌ current_period_start is None or missing!")
        
        # Clean up
        stripe.Subscription.delete(subscription.id)
        stripe.Customer.delete(customer.id)
        print(f"✅ Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_subscription_creation()
