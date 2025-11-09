
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {

    'process-affiliate-commissions': {
        'task': 'apps.affiliates.tasks.process_affiliate_commissions',
        'schedule': crontab(hour=2, minute=0),
        'options': {
            'expires': 3600, 
        }
    },
    
    'update-affiliate-stats': {
        'task': 'apps.affiliates.tasks.update_affiliate_stats',
        'schedule': crontab(hour=3, minute=0),
        'options': {
            'expires': 1800,
        }
    },
    
    'send-commission-notifications': {
        'task': 'apps.affiliates.tasks.send_commission_notifications',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
        'options': {
            'expires': 7200,
        }
    },
    
    'cleanup-old-commissions': {
        'task': 'apps.affiliates.tasks.cleanup_old_commissions',
        'schedule': crontab(hour=1, minute=0, day_of_month=1), 
        'options': {
            'expires': 3600,
        }
    },
}

CELERY_TIMEZONE = 'UTC'

CELERY_TASK_ROUTES = {
    'apps.affiliates.tasks.*': {'queue': 'affiliates'},
}

CELERY_TASK_DEFAULT_PRIORITY = 5
CELERY_TASK_ROUTES_PRIORITY = {
    'apps.affiliates.tasks.process_affiliate_commissions': 8,
    'apps.affiliates.tasks.update_affiliate_stats': 6,
    'apps.affiliates.tasks.send_commission_notifications': 4,
    'apps.affiliates.tasks.cleanup_old_commissions': 2,
}
