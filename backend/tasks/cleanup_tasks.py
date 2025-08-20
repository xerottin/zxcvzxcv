import os

import httpx
from celery import current_app
from celery.utils.log import get_task_logger
from core.settings import settings

logger = get_task_logger(__name__)


@current_app.task(bind=True, max_retries=3)
def cleanup_via_api(self, cleanup_type="unverified_users", days_threshold=7, dry_run=False, force=False):
    try:
        # admin_token = os.getenv("ADMIN_API_TOKEN")
        # if not admin_token:
        #     raise Exception("ADMIN_API_TOKEN not configured")

        # headers = {
        #     "Authorization": f"Bearer {admin_token}",
        #     "Content-Type": "application/json"
        # }

        payload = {
            "cleanup_type": cleanup_type,
            "days_threshold": days_threshold,
            "dry_run": dry_run,
            "force": force
        }

        with httpx.Client() as client:
            response = client.post(
                f"{settings.API_BASE_URL}/api/tasks/execute",
                json=payload,
                # headers=headers,
                timeout=60  # 1 minute timeout
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Cleanup completed via API: {result['message']}")
                return result
            else:
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

    except Exception as exc:
        logger.error(f"Cleanup via API failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@current_app.task(bind=True, max_retries=3)
def cleanup_unverified_users(self):
    return cleanup_via_api(
        cleanup_type="unverified_users",
        days_threshold=7,
        dry_run=False,
        force=False
    )


@current_app.task(bind=True, max_retries=3)
def weekly_comprehensive_cleanup(self):
    return cleanup_via_api(
        cleanup_type="all",
        days_threshold=30,
        dry_run=False,
        force=True
    )


@current_app.task(bind=True, max_retries=3)
def cleanup_expired_codes(self):
    return cleanup_via_api(
        cleanup_type="expired_codes",
        days_threshold=30,
        dry_run=False,
        force=False
    )
