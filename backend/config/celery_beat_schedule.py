"""
Celery Beat Schedule Configuration
Defines periodic tasks for Hotel PMS
"""

from celery.schedules import crontab

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    # Clean up expired tokens daily at 2 AM
    'cleanup-expired-tokens': {
        'task': 'apps.core.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),
        'options': {
            'expires': 3600,  # Task expires after 1 hour
        }
    },
    
    # Clean up old activity logs weekly on Sunday at 3 AM
    'cleanup-old-activity-logs': {
        'task': 'apps.core.tasks.cleanup_old_activity_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
        'kwargs': {'days': 90},  # Keep 90 days of logs
        'options': {
            'expires': 7200,
        }
    },
    
    # Generate night audit daily at 11:30 PM
    'generate-night-audit': {
        'task': 'apps.core.tasks.generate_night_audit_task',
        'schedule': crontab(hour=23, minute=30),
        'options': {
            'expires': 1800,  # Must complete within 30 minutes
        }
    },
    
    # Send reservation reminders daily at 9 AM
    'send-reservation-reminders': {
        'task': 'apps.core.tasks.send_reservation_reminder_task',
        'schedule': crontab(hour=9, minute=0),
        'options': {
            'expires': 3600,
        }
    },
    
    # Generate daily reports at 1 AM
    'generate-daily-reports': {
        'task': 'apps.core.tasks.generate_daily_reports_task',
        'schedule': crontab(hour=1, minute=0),
        'options': {
            'expires': 3600,
        }
    },
    
    # Health check every 5 minutes (monitor system health)
    # 'system-health-check': {
    #     'task': 'apps.core.tasks.system_health_check',
    #     'schedule': 300.0,  # 5 minutes in seconds
    # },
}
