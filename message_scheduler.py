"""
Message scheduler using APScheduler for managing deletion jobs.

Handles scheduling and execution of message deletion operations.
"""

import logging
from typing import Optional, Callable
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from telegram import Bot
from telegram.error import TelegramError


logger = logging.getLogger(__name__)


class MessageScheduler:
    """Manages scheduled message deletions."""

    def __init__(self):
        """Initialize the APScheduler."""
        self.scheduler = AsyncIOScheduler()
        self.bot: Optional[Bot] = None
        self.job_ids: dict[str, str] = {}  # Track job IDs to prevent duplicates

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Message scheduler started")

    def shutdown(self) -> None:
        """Shutdown the scheduler and clear all jobs."""
        self.scheduler.shutdown(wait=True)
        logger.info("Message scheduler shutdown complete")

    def schedule_message_deletion(
        self,
        group_id: int,
        message_id: int,
        delete_after_seconds: int,
        bot: Bot,
    ) -> bool:
        """
        Schedule a message for deletion.
        
        Args:
            group_id: The Telegram group ID
            message_id: The message ID to delete
            delete_after_seconds: Seconds until deletion
            bot: The Telegram Bot instance
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        try:
            # Create unique job ID
            job_id = f"{group_id}_{message_id}"
            
            # Check if message is already scheduled for deletion
            if job_id in self.job_ids:
                logger.debug(f"Message {message_id} already scheduled for deletion")
                return False

            # Calculate run time
            run_time = datetime.now() + timedelta(seconds=delete_after_seconds)

            # Schedule the job
            job = self.scheduler.add_job(
                func=self._delete_message,
                trigger=DateTrigger(run_time=run_time),
                args=(group_id, message_id, bot),
                id=job_id,
                name=f"Delete message {message_id} in group {group_id}",
                replace_existing=True,
                coalesce=True,
                max_instances=1,
            )

            self.job_ids[job_id] = job.id
            logger.debug(
                f"Message {message_id} scheduled for deletion in {delete_after_seconds}s "
                f"(at {run_time})"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error scheduling message {message_id} for deletion: {e}",
                exc_info=True,
            )
            return False

    def cancel_message_deletion(self, group_id: int, message_id: int) -> bool:
        """
        Cancel a scheduled message deletion.
        
        Args:
            group_id: The Telegram group ID
            message_id: The message ID
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            job_id = f"{group_id}_{message_id}"
            
            if job_id not in self.job_ids:
                return False

            self.scheduler.remove_job(self.job_ids[job_id])
            del self.job_ids[job_id]
            logger.debug(f"Cancelled deletion for message {message_id}")
            return True

        except Exception as e:
            logger.error(f"Error cancelling deletion for message {message_id}: {e}")
            return False

    def cancel_all_jobs(self) -> int:
        """
        Cancel all scheduled jobs.
        
        Returns:
            Number of jobs cancelled
        """
        try:
            count = len(self.job_ids)
            self.scheduler.remove_all_jobs()
            self.job_ids.clear()
            logger.info(f"Cancelled all {count} scheduled jobs")
            return count
        except Exception as e:
            logger.error(f"Error cancelling all jobs: {e}")
            return 0

    async def _delete_message(self, group_id: int, message_id: int, bot: Bot) -> None:
        """
        Delete a message. This is called by the scheduler.
        
        Args:
            group_id: The Telegram group ID
            message_id: The message ID to delete
            bot: The Telegram Bot instance
        """
        try:
            await bot.delete_message(
                chat_id=group_id,
                message_id=message_id,
            )
            logger.info(f"Deleted message {message_id} from group {group_id}")

        except TelegramError as e:
            if "message to delete not found" in str(e).lower():
                logger.debug(
                    f"Message {message_id} already deleted or not found in group {group_id}"
                )
            elif "not enough rights" in str(e).lower():
                logger.warning(
                    f"Bot doesn't have permission to delete message {message_id} "
                    f"in group {group_id}"
                )
            else:
                logger.warning(
                    f"Telegram error deleting message {message_id}: {e}"
                )

        except Exception as e:
            logger.error(
                f"Unexpected error deleting message {message_id}: {e}",
                exc_info=True,
            )

        finally:
            # Clean up job tracking
            job_id = f"{group_id}_{message_id}"
            if job_id in self.job_ids:
                del self.job_ids[job_id]

    def get_pending_jobs_count(self) -> int:
        """
        Get count of pending deletion jobs.
        
        Returns:
            Number of pending jobs
        """
        return len(self.job_ids)

    def get_pending_jobs_info(self) -> list[dict[str, str | int]]:
        """
        Get information about pending deletion jobs.
        
        Returns:
            List of job information dictionaries
        """
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                "job_id": job.id,
                "next_run": str(job.next_run_time),
                "name": job.name,
            })
        return jobs_info
