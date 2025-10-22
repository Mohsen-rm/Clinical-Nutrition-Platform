"""
مهام Celery لمعالجة العمولات التلقائية
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
    مهمة معالجة العمولات التلقائية
    تعمل يومياً لمعالجة المدفوعات الجديدة
    """
    logger.info("🚀 بدء معالجة العمولات التلقائية")
    
    processed_count = 0
    total_commission_amount = Decimal('0.00')
    commission_rate = Decimal('0.30')  # 30%
    
    try:
        # البحث عن المدفوعات الناجحة التي لم تتم معالجة عمولاتها
        new_payments = Payment.objects.filter(
            status='succeeded',
            affiliate_commission__isnull=True,  # لم تتم معالجة العمولة
            subscription__user__referred_by__isnull=False,  # المستخدم تم إحالته
            created_at__gte=timezone.now() - timedelta(days=7)  # آخر أسبوع
        ).select_related(
            'subscription__user__referred_by',
            'subscription__plan'
        )
        
        logger.info(f"📊 تم العثور على {new_payments.count()} مدفوعة جديدة")
        
        for payment in new_payments:
            try:
                with transaction.atomic():
                    subscription = payment.subscription
                    referred_user = subscription.user
                    affiliate = referred_user.referred_by
                    
                    if not affiliate:
                        continue
                    
                    # حساب العمولة (30% من المبلغ)
                    commission_amount = payment.amount * commission_rate
                    
                    # إنشاء سجل العمولة
                    commission = AffiliateCommission.objects.create(
                        affiliate=affiliate,
                        referred_user=referred_user,
                        payment=payment,
                        commission_amount=commission_amount,
                        commission_percentage=commission_rate * 100,
                        commission_type='subscription',
                        status='pending'
                    )
                    
                    # تحديث المدفوعة لتسجيل العمولة
                    payment.affiliate_commission = commission_amount
                    payment.save()
                    
                    # تحديث إحصائيات الشريك
                    stats, created = AffiliateStats.objects.get_or_create(user=affiliate)
                    stats.update_stats()
                    
                    processed_count += 1
                    total_commission_amount += commission_amount
                    
                    logger.info(f"✅ تم إنشاء عمولة: {affiliate.email} - ${commission_amount}")
                    
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة المدفوعة {payment.id}: {str(e)}")
                continue
        
        logger.info(f"✅ انتهت معالجة العمولات: {processed_count} عمولة، إجمالي ${total_commission_amount}")
        
        return {
            'processed_count': processed_count,
            'total_amount': float(total_commission_amount),
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة العمولات: {str(e)}")
        return {
            'processed_count': 0,
            'total_amount': 0,
            'status': 'error',
            'error': str(e)
        }

@shared_task
def update_affiliate_stats():
    """
    مهمة تحديث إحصائيات الشركاء
    تعمل يومياً لتحديث جميع الإحصائيات
    """
    logger.info("🔄 بدء تحديث إحصائيات الشركاء")
    
    try:
        # الحصول على جميع الشركاء
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
                    logger.info(f"➕ تم إنشاء إحصائيات جديدة: {affiliate.email}")
                
            except Exception as e:
                logger.error(f"❌ خطأ في تحديث إحصائيات {affiliate.email}: {str(e)}")
                continue
        
        logger.info(f"✅ تم تحديث إحصائيات {updated_count} شريك")
        
        return {
            'updated_count': updated_count,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث الإحصائيات: {str(e)}")
        return {
            'updated_count': 0,
            'status': 'error',
            'error': str(e)
        }

@shared_task
def send_commission_notifications():
    """
    مهمة إرسال إشعارات العمولات
    تعمل أسبوعياً لإرسال تقارير للشركاء
    """
    logger.info("📧 بدء إرسال إشعارات العمولات")
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # الحصول على الشركاء الذين لديهم عمولات معلقة
        affiliates_with_pending = User.objects.filter(
            affiliate_commissions__status='pending'
        ).distinct()
        
        sent_count = 0
        for affiliate in affiliates_with_pending:
            try:
                # حساب العمولات المعلقة
                pending_commissions = AffiliateCommission.objects.filter(
                    affiliate=affiliate,
                    status='pending'
                )
                total_pending = sum(c.commission_amount for c in pending_commissions)
                
                if total_pending > 0:
                    # إرسال إيميل
                    subject = f"تقرير العمولات الأسبوعي - Clinical Nutrition Platform"
                    message = f"""
مرحباً {affiliate.first_name or affiliate.email},

لديك عمولات معلقة في نظام الشراكة:

💰 إجمالي العمولات المعلقة: ${total_pending:.2f}
📊 عدد العمولات: {pending_commissions.count()}

يمكنك طلب سحب العمولات من خلال لوحة الشراكة في الموقع.

شكراً لك على شراكتك معنا!

فريق Clinical Nutrition Platform
                    """
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [affiliate.email],
                        fail_silently=True
                    )
                    
                    sent_count += 1
                    logger.info(f"📧 تم إرسال إشعار إلى: {affiliate.email}")
                
            except Exception as e:
                logger.error(f"❌ خطأ في إرسال إشعار إلى {affiliate.email}: {str(e)}")
                continue
        
        logger.info(f"✅ تم إرسال {sent_count} إشعار")
        
        return {
            'sent_count': sent_count,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الإشعارات: {str(e)}")
        return {
            'sent_count': 0,
            'status': 'error',
            'error': str(e)
        }

@shared_task
def cleanup_old_commissions():
    """
    مهمة تنظيف العمولات القديمة
    تعمل شهرياً لأرشفة العمولات القديمة
    """
    logger.info("🧹 بدء تنظيف العمولات القديمة")
    
    try:
        # أرشفة العمولات المدفوعة الأقدم من سنة
        old_date = timezone.now() - timedelta(days=365)
        old_commissions = AffiliateCommission.objects.filter(
            status='paid',
            paid_at__lt=old_date
        )
        
        archived_count = old_commissions.count()
        
        # يمكن إضافة منطق الأرشفة هنا
        # مثل نقل البيانات إلى جدول أرشيف
        
        logger.info(f"📦 تم العثور على {archived_count} عمولة قديمة للأرشفة")
        
        return {
            'archived_count': archived_count,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في تنظيف العمولات: {str(e)}")
        return {
            'archived_count': 0,
            'status': 'error',
            'error': str(e)
        }
