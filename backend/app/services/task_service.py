"""
Google Cloud Tasks service for background job scheduling.

This service handles:
- Insurance data synchronization
- Claims imports
- Provider portal syncs
- Scheduled tasks (daily sync, token refresh)
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

logger = logging.getLogger(__name__)


class TaskService:
    """
    Google Cloud Tasks service for background job scheduling.

    Usage:
        task_service = TaskService()
        await task_service.create_insurance_sync_task(connection_id="abc123")
    """

    def __init__(self):
        """Initialize Cloud Tasks client."""
        self.client = tasks_v2.CloudTasksClient()
        self.project = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_REGION", "us-central1")
        self.queue = os.getenv("CLOUD_TASKS_QUEUE", "insurance-sync-queue")
        self.backend_url = os.getenv("BACKEND_URL", "https://api.medbilldozer.com")

        if not self.project:
            logger.warning("GCP_PROJECT_ID not set. Task service will not work.")

    def _get_queue_path(self, queue_name: Optional[str] = None) -> str:
        """Get the full queue path."""
        queue = queue_name or self.queue
        return self.client.queue_path(self.project, self.location, queue)

    async def create_insurance_sync_task(
        self, connection_id: str, delay_seconds: int = 0, retry_count: int = 0
    ) -> str:
        """
        Create background task to sync insurance data.

        Args:
            connection_id: Insurance connection ID to sync
            delay_seconds: Delay before execution (default: immediate)
            retry_count: Current retry attempt (for exponential backoff)

        Returns:
            Task name/ID
        """
        parent = self._get_queue_path()

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.backend_url}/api/insurance/sync/{connection_id}",
                "headers": {
                    "Content-Type": "application/json",
                    "X-CloudTasks-TaskRetryCount": str(retry_count),
                },
                "body": json.dumps(
                    {
                        "connection_id": connection_id,
                        "triggered_by": "system",
                        "retry_count": retry_count,
                    }
                ).encode(),
            }
        }

        # Add delay if specified
        if delay_seconds > 0:
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(datetime.utcnow() + timedelta(seconds=delay_seconds))
            task["schedule_time"] = timestamp

        try:
            response = self.client.create_task(request={"parent": parent, "task": task})
            logger.info(f"Created insurance sync task: {response.name}")
            return response.name
        except Exception as e:
            logger.error(f"Failed to create insurance sync task: {e}")
            raise

    async def create_claims_check_task(
        self, connection_id: str, start_date: Optional[str] = None
    ) -> str:
        """
        Create task to check for new claims.

        Args:
            connection_id: Insurance connection ID
            start_date: Check for claims after this date (ISO format)

        Returns:
            Task name/ID
        """
        parent = self._get_queue_path()

        payload = {
            "connection_id": connection_id,
            "start_date": start_date or (datetime.utcnow() - timedelta(days=7)).isoformat(),
        }

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.backend_url}/api/insurance/claims/check/{connection_id}",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
            }
        }

        try:
            response = self.client.create_task(request={"parent": parent, "task": task})
            logger.info(f"Created claims check task: {response.name}")
            return response.name
        except Exception as e:
            logger.error(f"Failed to create claims check task: {e}")
            raise

    async def create_token_refresh_task(self, connection_id: str, delay_hours: int = 23) -> str:
        """
        Create task to refresh OAuth token before expiry.

        Args:
            connection_id: Insurance connection ID
            delay_hours: Hours before token expiry to refresh (default: 23)

        Returns:
            Task name/ID
        """
        parent = self._get_queue_path()

        # Schedule for 23 hours before expiry
        delay_seconds = delay_hours * 3600

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.backend_url}/api/insurance/refresh-token/{connection_id}",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"connection_id": connection_id}).encode(),
            },
            "schedule_time": timestamp_pb2.Timestamp(),
        }

        task["schedule_time"].FromDatetime(datetime.utcnow() + timedelta(seconds=delay_seconds))

        try:
            response = self.client.create_task(request={"parent": parent, "task": task})
            logger.info(f"Created token refresh task: {response.name} (in {delay_hours}h)")
            return response.name
        except Exception as e:
            logger.error(f"Failed to create token refresh task: {e}")
            raise

    async def create_document_processing_task(
        self, document_id: str, priority: str = "normal"
    ) -> str:
        """
        Create task to process uploaded document.

        Args:
            document_id: Document ID to process
            priority: Task priority ('low', 'normal', 'high')

        Returns:
            Task name/ID
        """
        parent = self._get_queue_path()

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.backend_url}/api/documents/process/{document_id}",
                "headers": {"Content-Type": "application/json", "X-Task-Priority": priority},
                "body": json.dumps({"document_id": document_id, "priority": priority}).encode(),
            }
        }

        try:
            response = self.client.create_task(request={"parent": parent, "task": task})
            logger.info(f"Created document processing task: {response.name}")
            return response.name
        except Exception as e:
            logger.error(f"Failed to create document processing task: {e}")
            raise

    async def create_alert_check_task(
        self, user_id: str, alert_types: Optional[list] = None
    ) -> str:
        """
        Create task to check for user alerts.

        Args:
            user_id: User ID to check alerts for
            alert_types: Specific alert types to check (default: all)

        Returns:
            Task name/ID
        """
        parent = self._get_queue_path()

        payload = {"user_id": user_id, "alert_types": alert_types or ["all"]}

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.backend_url}/api/alerts/check/{user_id}",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
            }
        }

        try:
            response = self.client.create_task(request={"parent": parent, "task": task})
            logger.info(f"Created alert check task: {response.name}")
            return response.name
        except Exception as e:
            logger.error(f"Failed to create alert check task: {e}")
            raise

    async def schedule_daily_sync(self) -> None:
        """
        Schedule daily sync for all active insurance connections.
        This should be called by Cloud Scheduler at 3 AM daily.
        """
        logger.info("Scheduling daily sync for all active connections...")

        # TODO: Implement daily sync scheduling
        # Will query all active connections and create sync tasks for each one
        logger.warning("Daily sync scheduling not yet implemented")

    async def cancel_task(self, task_name: str) -> bool:
        """
        Cancel a pending task.

        Args:
            task_name: Full task name (from create_task response)

        Returns:
            True if cancelled successfully
        """
        try:
            self.client.delete_task(name=task_name)
            logger.info(f"Cancelled task: {task_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_name}: {e}")
            return False


# Singleton instance
_task_service_instance = None


def get_task_service() -> TaskService:
    """Get singleton TaskService instance."""
    global _task_service_instance
    if _task_service_instance is None:
        _task_service_instance = TaskService()
    return _task_service_instance
