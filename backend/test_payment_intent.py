#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.conf import settings
from apps.subscriptions.models import SubscriptionPlan
import stripe

def test_payment_intent():
    """Test payment intent creation"""
    
    # Check Stripe settings
    print("=== STRIPE SETTINGS ===")
    print(f"Publishable Key: {settings.STRIPE_PUBLISHABLE_KEY[:20]}...")
    print(f"Secret Key: {settings.STRIPE_SECRET_KEY[:20]}...")
    
    # Set Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Get a plan
    try:
        plan = SubscriptionPlan.objects.first()
        if not plan:
            print("❌ No subscription plans found")
            return
        
        print(f"\n=== TESTING PLAN ===")
        print(f"Plan: {plan.name}")
        print(f"Price: ${plan.price} {plan.currency}")
        
        # Calculate amount in cents
        amount = int(float(plan.price) * 100)
        currency = plan.currency.lower()
        
        print(f"Amount in cents: {amount}")
        print(f"Currency: {currency}")
        
        # Test Stripe API
        print(f"\n=== CREATING PAYMENT INTENT ===")
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                'plan_id': plan.id,
                'plan_name': plan.name
            }
        )
        
        print(f"✅ Payment Intent created successfully!")
        print(f"ID: {intent.id}")
        print(f"Amount: {intent.amount} cents")
        print(f"Currency: {intent.currency}")
        print(f"Status: {intent.status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_payment_intent()
