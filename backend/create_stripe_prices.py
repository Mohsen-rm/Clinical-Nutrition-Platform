#!/usr/bin/env python
"""
Script to create Stripe products and prices for the Clinical Nutrition Platform
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

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_products_and_prices():
    """Create Stripe products and prices for all subscription plans"""
    
    plans_data = [
        {
            'name': 'Basic Plan',
            'description': 'Basic nutrition planning with essential features',
            'price': 29.00,
            'plan_type': 'basic',
            'features': [
                'Basic nutrition calculator',
                'Standard meal plans',
                'Email support',
                'Mobile app access'
            ]
        },
        {
            'name': 'Professional Plan', 
            'description': 'Advanced nutrition planning for healthcare professionals',
            'price': 79.00,
            'plan_type': 'professional',
            'features': [
                'Advanced nutrition calculator',
                'Custom meal plans',
                'Disease-specific adjustments',
                'Priority support',
                'WhatsApp integration',
                'Patient management tools'
            ]
        },
        {
            'name': 'Enterprise Plan',
            'description': 'Complete nutrition platform for clinics and hospitals',
            'price': 149.00,
            'plan_type': 'premium',
            'features': [
                'All Professional features',
                'Multi-user access',
                'Advanced analytics',
                'API access',
                'Custom integrations',
                'Dedicated support'
            ]
        }
    ]
    
    print("Creating Stripe products and prices...")
    
    for plan_data in plans_data:
        try:
            # Create Stripe product
            product = stripe.Product.create(
                name=plan_data['name'],
                description=plan_data['description'],
                metadata={
                    'plan_type': plan_data['plan_type']
                }
            )
            
            print(f"✅ Created product: {product.id} - {plan_data['name']}")
            
            # Create Stripe price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(plan_data['price'] * 100),  # Convert to cents
                currency='usd',
                recurring={'interval': 'month'},
                metadata={
                    'plan_type': plan_data['plan_type']
                }
            )
            
            print(f"✅ Created price: {price.id} - ${plan_data['price']}/month")
            
            # Update or create SubscriptionPlan in database
            subscription_plan, created = SubscriptionPlan.objects.update_or_create(
                plan_type=plan_data['plan_type'],
                defaults={
                    'name': plan_data['name'],
                    'description': plan_data['description'],
                    'price': plan_data['price'],
                    'currency': 'USD',
                    'stripe_price_id': price.id,
                    'stripe_product_id': product.id,
                    'is_active': True,
                    'features': plan_data['features']
                }
            )
            
            action = "Created" if created else "Updated"
            print(f"✅ {action} database plan: {subscription_plan.name}")
            print("-" * 50)
            
        except stripe.StripeError as e:
            print(f"❌ Stripe error for {plan_data['name']}: {str(e)}")
        except Exception as e:
            print(f"❌ Database error for {plan_data['name']}: {str(e)}")
    
    print("\n📋 Final subscription plans in database:")
    plans = SubscriptionPlan.objects.all().order_by('price')
    for plan in plans:
        print(f"ID: {plan.id}")
        print(f"Name: {plan.name}")
        print(f"Price: ${plan.price}/month")
        print(f"Stripe Price ID: {plan.stripe_price_id}")
        print(f"Stripe Product ID: {plan.stripe_product_id}")
        print(f"Features: {len(plan.features)} features")
        print("-" * 30)

if __name__ == '__main__':
    print("🚀 Starting Stripe products and prices creation...")
    print(f"Using Stripe API Key: {stripe.api_key[:12]}...")
    
    create_stripe_products_and_prices()
    
    print("\n✅ Done! You can now test the subscription flow.")
    print("💡 Test with card: 4242424242424242")
