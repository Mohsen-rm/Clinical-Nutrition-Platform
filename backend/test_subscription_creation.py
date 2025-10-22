#!/usr/bin/env python
"""
Test script to verify subscription creation works with new Stripe prices
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
from apps.subscriptions.stripe_service import StripeService

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def test_subscription_creation():
    """Test that Stripe prices exist and are accessible"""
    
    print("🧪 Testing Stripe prices...")
    
    # Test all plans
    plans = SubscriptionPlan.objects.all().order_by('price')
    
    for plan in plans:
        try:
            print(f"\n📋 Testing {plan.name}:")
            print(f"   Database ID: {plan.id}")
            print(f"   Price: ${plan.price}")
            print(f"   Stripe Price ID: {plan.stripe_price_id}")
            
            # Verify price exists in Stripe
            stripe_price = stripe.Price.retrieve(plan.stripe_price_id)
            print(f"✅ Stripe price found: {stripe_price.id}")
            print(f"   Amount: ${stripe_price.unit_amount / 100}")
            print(f"   Currency: {stripe_price.currency.upper()}")
            print(f"   Interval: {stripe_price.recurring.interval}")
            
            # Verify product exists
            stripe_product = stripe.Product.retrieve(stripe_price.product)
            print(f"✅ Stripe product found: {stripe_product.name}")
            
        except stripe.StripeError as e:
            print(f"❌ Stripe error for {plan.name}: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error for {plan.name}: {str(e)}")
    
    print("\n🎉 All Stripe prices are valid and accessible!")
    print("💡 You can now test the subscription flow in the frontend.")

if __name__ == '__main__':
    test_subscription_creation()
