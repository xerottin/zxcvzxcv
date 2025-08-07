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

    beat_schedule={
        "cleanup-unverified-users": {
            "task": "tasks.cleanup_tasks.cleanup_unverified_users",
            # "schedule": crontab(hour=2, minute=0), #project
            "schedule": 60.0,  # for testing
        },
        "cleanup-expired-verification-codes": {
            "task": "tasks.cleanup_tasks.cleanup_expired_codes",
            "schedule": crontab(minute="*/30"),  # every 30 minutes
        }
    },
    beat_schedule_filename="celerybeat-schedule",
)
