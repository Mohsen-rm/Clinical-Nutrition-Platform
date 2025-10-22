import stripe
from django.conf import settings
from django.utils import timezone
from .models import Subscription, SubscriptionPlan, Payment
from apps.affiliates.models import AffiliateCommission

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def create_customer(user):
        """Create a Stripe customer for the user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    'user_id': user.id,
                    'user_type': user.user_type
                }
            )
            return customer
        except stripe.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    @staticmethod
    def create_subscription(user, plan_id, payment_method_id):
        """Create a subscription for the user"""
        try:
            print(f"🔍 Creating subscription for user {user.id}, plan {plan_id}, payment_method {payment_method_id}")
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            print(f"✅ Plan found: {plan.name} - {plan.stripe_price_id}")
            
            # Create or get customer
            customer = StripeService.create_customer(user)
            print(f"✅ Customer created: {customer.id}")
            
            # Try to attach payment method to customer (handle if already attached)
            try:
                stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=customer.id,
                )
            except stripe.StripeError as e:
                # If payment method is already attached or has issues, 
                # we'll still try to create the subscription
                print(f"PaymentMethod attach warning: {str(e)}")
            
            # Set as default payment method
            try:
                stripe.Customer.modify(
                    customer.id,
                    invoice_settings={
                        'default_payment_method': payment_method_id,
                    },
                )
            except stripe.StripeError as e:
                print(f"Customer modify warning: {str(e)}")
            
            # Create subscription with immediate payment
            print(f"🔍 Creating Stripe subscription...")
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{
                    'price': plan.stripe_price_id,
                }],
                default_payment_method=payment_method_id,
                expand=['latest_invoice.payment_intent'],
                metadata={
                    'user_id': user.id,
                    'plan_id': plan.id,
                }
            )
            print(f"✅ Stripe subscription created: {subscription.id}")
            print(f"   Status: {subscription.status}")
            print(f"   Current period start: {getattr(subscription, 'current_period_start', 'Not available')}")
            print(f"   Current period end: {getattr(subscription, 'current_period_end', 'Not available')}")
            
            # Save subscription to database
            # Handle current_period_start and current_period_end safely
            current_period_start = None
            current_period_end = None
            
            if hasattr(subscription, 'current_period_start') and subscription.current_period_start:
                current_period_start = timezone.datetime.fromtimestamp(
                    subscription.current_period_start, tz=timezone.utc
                )
            
            if hasattr(subscription, 'current_period_end') and subscription.current_period_end:
                current_period_end = timezone.datetime.fromtimestamp(
                    subscription.current_period_end, tz=timezone.utc
                )
            
            # If periods are not available, use current time and add 30 days
            if not current_period_start:
                current_period_start = timezone.now()
            if not current_period_end:
                from datetime import timedelta
                current_period_end = current_period_start + timedelta(days=30)
            
            print(f"🔍 Saving subscription to database...")
            print(f"   User: {user.id}")
            print(f"   Plan: {plan.id}")
            print(f"   Stripe Subscription ID: {subscription.id}")
            print(f"   Customer ID: {customer.id}")
            print(f"   Status: {subscription.status}")
            print(f"   Period start: {current_period_start}")
            print(f"   Period end: {current_period_end}")
            
            db_subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                stripe_subscription_id=subscription.id,
                stripe_customer_id=customer.id,
                status=subscription.status,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
            )
            print(f"✅ Database subscription created: {db_subscription.id}")
            
            # Get client_secret safely
            client_secret = None
            try:
                if hasattr(subscription, 'latest_invoice') and subscription.latest_invoice:
                    if hasattr(subscription.latest_invoice, 'payment_intent') and subscription.latest_invoice.payment_intent:
                        client_secret = subscription.latest_invoice.payment_intent.client_secret
                        print(f"✅ Client secret obtained: {client_secret[:20]}...")
                    else:
                        print("⚠️ No payment_intent found in latest_invoice")
                else:
                    print("⚠️ No latest_invoice found in subscription")
            except Exception as e:
                print(f"⚠️ Could not get client_secret: {str(e)}")
            
            return {
                'subscription': db_subscription,
                'client_secret': client_secret,
                'subscription_id': subscription.id
            }
            
        except SubscriptionPlan.DoesNotExist:
            print(f"❌ Subscription plan not found: {plan_id}")
            raise Exception("Invalid subscription plan")
        except stripe.StripeError as e:
            print(f"❌ Stripe error: {str(e)}")
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error in create_subscription: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Subscription creation failed: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id, cancel_at_period_end=True):
        """Cancel a subscription"""
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            
            if cancel_at_period_end:
                # Cancel at period end
                stripe_sub = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                subscription.cancel_at_period_end = True
            else:
                # Cancel immediately
                stripe_sub = stripe.Subscription.delete(subscription_id)
                subscription.status = 'canceled'
                subscription.canceled_at = timezone.now()
            
            subscription.save()
            return subscription
            
        except Subscription.DoesNotExist:
            raise Exception("Subscription not found")
        except stripe.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def handle_webhook_event(event):
        """Handle Stripe webhook events"""
        try:
            if event['type'] == 'invoice.payment_succeeded':
                StripeService._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                StripeService._handle_payment_failed(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                StripeService._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                StripeService._handle_subscription_deleted(event['data']['object'])
                
        except Exception as e:
            print(f"Error handling webhook event: {str(e)}")
    
    @staticmethod
    def _handle_payment_succeeded(invoice):
        """Handle successful payment"""
        subscription_id = invoice['subscription']
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            
            # Create payment record
            payment = Payment.objects.create(
                subscription=subscription,
                stripe_payment_intent_id=invoice['payment_intent'],
                amount=invoice['amount_paid'] / 100,  # Convert from cents
                currency=invoice['currency'].upper(),
                status='succeeded'
            )
            
            # Calculate and create affiliate commission if user was referred
            if subscription.user.referred_by:
                commission_amount = payment.amount * 0.30  # 30% commission
                payment.affiliate_commission = commission_amount
                payment.save()
                
                # Create affiliate commission record
                AffiliateCommission.objects.create(
                    affiliate=subscription.user.referred_by,
                    referred_user=subscription.user,
                    payment=payment,
                    commission_amount=commission_amount,
                    commission_type='subscription'
                )
            
        except Subscription.DoesNotExist:
            print(f"Subscription not found for payment: {subscription_id}")
    
    @staticmethod
    def _handle_payment_failed(invoice):
        """Handle failed payment"""
        subscription_id = invoice['subscription']
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = 'past_due'
            subscription.save()
            
        except Subscription.DoesNotExist:
            print(f"Subscription not found for failed payment: {subscription_id}")
    
    @staticmethod
    def _handle_subscription_updated(stripe_subscription):
        """Handle subscription updates"""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=stripe_subscription['id']
            )
            subscription.status = stripe_subscription['status']
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                stripe_subscription['current_period_start'], tz=timezone.utc
            )
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                stripe_subscription['current_period_end'], tz=timezone.utc
            )
            subscription.cancel_at_period_end = stripe_subscription.get('cancel_at_period_end', False)
            subscription.save()
            
        except Subscription.DoesNotExist:
            print(f"Subscription not found for update: {stripe_subscription['id']}")
    
    @staticmethod
    def _handle_subscription_deleted(stripe_subscription):
        """Handle subscription deletion"""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=stripe_subscription['id']
            )
            subscription.status = 'canceled'
            subscription.canceled_at = timezone.now()
            subscription.save()
            
        except Subscription.DoesNotExist:
            print(f"Subscription not found for deletion: {stripe_subscription['id']}")
