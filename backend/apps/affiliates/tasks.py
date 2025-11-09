"""
Celery tasks for processing automatic commissions
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
import logging

from apps.subscriptions.models import Payment
from .models import AffiliateCommission, AffiliateStats

logger = logging.getLogger(__name__)

@shared_task
def process_affiliate_commissions():
    """
    Automatic commission processing task
    Runs daily to process new payments
    """
    logger.info("🚀 Starting automatic commission processing")
    
    processed_count = 0
    total_commission_amount = Decimal('0.00')
    commission_rate = Decimal('0.30')  # 30%
    
    try:
        # Find successful payments whose commissions haven't been processed
        new_payments = Payment.objects.filter(
            status='succeeded',
            affiliate_commission__isnull=True,  # Commission not processed
            subscription__user__referred_by__isnull=False,  # User was referred
            created_at__gte=timezone.now() - timedelta(days=7)  # Last week
        ).select_related(
            'subscription__user__referred_by',
            'subscription__plan'
        )
        
        logger.info(f"📊 Found {new_payments.count()} new payments")
        
        for payment in new_payments:
            try:
                with transaction.atomic():
                    subscription = payment.subscription
                    referred_user = subscription.user
                    affiliate = referred_user.referred_by
                    
                    if not affiliate:
                        continue
                    
                    # Calculate commission (30% of amount)
                    commission_amount = payment.amount * commission_rate
                    
                    # Create commission record
                    commission = AffiliateCommission.objects.create(
                        affiliate=affiliate,
                        referred_user=referred_user,
                        payment=payment,
                        commission_amount=commission_amount,
                        commission_percentage=commission_rate * 100,
                        commission_type='subscription',
                        status='pending'
                    )
                    
                    # Update payment to record commission
                    payment.affiliate_commission = commission_amount
                    payment.save()
                    
                    # Update affiliate stats
                    stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
                    stats.update_stats()
                    
                    processed_count += 1
                    total_commission_amount += commission_amount
                    
                    logger.info(f"✅ Commission created: {affiliate.email} - ${commission_amount}")
                
            except Exception as e:
                logger.error(f"❌ Error processing payment {payment.id}: {str(e)}")
                continue
        
        logger.info(f"✅ Commission processing finished: {processed_count} commissions, total ${total_commission_amount}")
        
        return {
            'processed_count': processed_count,
            'total_amount': float(total_commission_amount),
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing commissions: {str(e)}")
        return {
            'processed_count': 0,
            'total_amount': 0,
            'status': 'error',
            'error': str(e)
        }

@shared_task
def update_affiliate_stats():
    """
    Task to update affiliate stats
    Runs daily to update all stats
    """
    logger.info("🔄 Starting affiliates stats update")
    
    try:
        # Get all affiliates
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        affiliates = User.objects.filter(
            affiliate_commissions__isnull=False
        ).distinct()
        
        updated_count = 0
        for affiliate in affiliates:
            try:
                stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
                stats.update_stats()
                updated_count += 1
                
                if created:
                    logger.info(f"➕ Created new stats: {affiliate.email}")
                
            except Exception as e:
                logger.error(f"❌ Error updating stats for {affiliate.email}: {str(e)}")
                continue
        
        logger.info(f"✅ Updated stats for {updated_count} affiliates")
        
        return {
            'updated_count': updated_count,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating stats: {str(e)}")
        return {
            'updated_count': 0,
            'status': 'error',
            'error': str(e)
        }

@shared_task
def send_commission_notifications():
    """
    Task to send commission notifications
    Runs weekly to send reports to affiliates
    """
    logger.info("📧 Starting commission notifications sending")
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get affiliates with pending commissions
        affiliates_with_pending = User.objects.filter(
            affiliate_commissions__status='pending'
        ).distinct()
        
        sent_count = 0
        for affiliate in affiliates_with_pending:
            try:
                # Calculate pending commissions
                pending_commissions = AffiliateCommission.objects.filter(
                    affiliate=affiliate,
                    status='pending'
                )
                total_pending = sum(c.commission_amount for c in pending_commissions)
                
                if total_pending > 0:
                    # Send email
                    subject = f"Weekly Commission Report - Clinical Nutrition Platform"
                    message = f"""
Hello {affiliate.first_name or affiliate.email},

You have pending commissions in the affiliate system:

💰 Total pending commissions: ${total_pending:.2f}
📊 Number of commissions: {pending_commissions.count()}

You can request a payout from the affiliate dashboard on the site.

Thank you for partnering with us!

Clinical Nutrition Platform Team
                    """
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [affiliate.email],
                        fail_silently=True
                    )
                    
                    sent_count += 1
                    logger.info(f"📧 Notification sent to: {affiliate.email}")
                
            except Exception as e:
                logger.error(f"❌ خطأ في إرسال إشعار إلى {affiliate.email}: {str(e)}")
                continue
        
        logger.info(f"✅ تم إرسال {sent_count} إشعار")
        
        return {
            'sent_count': sent_count,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ Error sending notifications: {str(e)}")
        return {
            'sent_count': 0,
            'status': 'error',
            'error': str(e)
        }

@shared_task
def cleanup_old_commissions():
    """
    Task to clean up old commissions
    Runs monthly to archive old commissions
    """
    logger.info("🧹 Starting old commissions cleanup")
    
    try:
        # Archive paid commissions older than a year
        old_date = timezone.now() - timedelta(days=365)
        old_commissions = AffiliateCommission.objects.filter(
            status='paid',
            paid_at__lt=old_date
        )
        
        archived_count = old_commissions.count()
        
        # Archiving logic can be added here
        # e.g., moving data to an archive table
        
        logger.info(f"📦 Found {archived_count} old commissions for archiving")
        
        return {
            'archived_count': archived_count,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up commissions: {str(e)}")
        return {
            'archived_count': 0,
            'status': 'error',
            'error': str(e)
        }
