from celery import Celery
from celery.schedules import crontab
from core.settings import settings

celery_app = Celery(
    "auth_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.cleanup_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    beat_schedule={
        # Weekly comprehensive cleanup (Every Monday at 2:00 AM UTC)
        "weekly-comprehensive-cleanup": {
            "task": "tasks.cleanup_tasks.weekly_comprehensive_cleanup",
            # "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Production schedule
            "schedule": 300.0,  # For testing: every 2 minutes
        },

        # Daily unverified users cleanup (Every day at 3:00 AM UTC)
        "daily-unverified-users-cleanup": {
            "task": "tasks.cleanup_tasks.cleanup_unverified_users",
            # "schedule": crontab(hour=3, minute=0),  # Production schedule
            "schedule": 300.0,  # For testing: every minute
        },

        # Frequent expired codes cleanup (Every 30 minutes)
        "cleanup-expired-verification-codes": {
            "task": "tasks.cleanup_tasks.cleanup_expired_codes",
            "schedule": crontab(minute="*/6"),  # Every 30 minutes
        }
    },
    beat_schedule_filename="celerybeat-schedule",
)

if __name__ == "__main__":
    celery_app.start()
