"""
إعدادات جدولة مهام Celery للعمولات
"""
from celery.schedules import crontab

# إعدادات المهام المجدولة
CELERY_BEAT_SCHEDULE = {
    # معالجة العمولات يومياً في الساعة 2:00 صباحاً
    'process-affiliate-commissions': {
        'task': 'apps.affiliates.tasks.process_affiliate_commissions',
        'schedule': crontab(hour=2, minute=0),  # يومياً الساعة 2:00 ص
        'options': {
            'expires': 3600,  # انتهاء صلاحية المهمة بعد ساعة
        }
    },
    
    # تحديث إحصائيات الشركاء يومياً في الساعة 3:00 صباحاً
    'update-affiliate-stats': {
        'task': 'apps.affiliates.tasks.update_affiliate_stats',
        'schedule': crontab(hour=3, minute=0),  # يومياً الساعة 3:00 ص
        'options': {
            'expires': 1800,  # انتهاء صلاحية المهمة بعد 30 دقيقة
        }
    },
    
    # إرسال إشعارات العمولات أسبوعياً يوم الاثنين الساعة 9:00 صباحاً
    'send-commission-notifications': {
        'task': 'apps.affiliates.tasks.send_commission_notifications',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # الاثنين 9:00 ص
        'options': {
            'expires': 7200,  # انتهاء صلاحية المهمة بعد ساعتين
        }
    },
    
    # تنظيف العمولات القديمة شهرياً في اليوم الأول الساعة 1:00 صباحاً
    'cleanup-old-commissions': {
        'task': 'apps.affiliates.tasks.cleanup_old_commissions',
        'schedule': crontab(hour=1, minute=0, day_of_month=1),  # أول كل شهر 1:00 ص
        'options': {
            'expires': 3600,  # انتهاء صلاحية المهمة بعد ساعة
        }
    },
}

# إعدادات المنطقة الزمنية
CELERY_TIMEZONE = 'UTC'

# إعدادات إضافية للمهام
CELERY_TASK_ROUTES = {
    'apps.affiliates.tasks.*': {'queue': 'affiliates'},
}

# إعدادات الأولوية
CELERY_TASK_DEFAULT_PRIORITY = 5
CELERY_TASK_ROUTES_PRIORITY = {
    'apps.affiliates.tasks.process_affiliate_commissions': 8,  # أولوية عالية
    'apps.affiliates.tasks.update_affiliate_stats': 6,
    'apps.affiliates.tasks.send_commission_notifications': 4,
    'apps.affiliates.tasks.cleanup_old_commissions': 2,  # أولوية منخفضة
}
