
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
        # Ensure no existing payment
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
