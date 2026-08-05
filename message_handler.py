"""
Message handlers for processing incoming Telegram messages.

Handles automatic scheduling of message deletion based on group settings.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from database import DatabaseManager
from scheduler.message_scheduler import MessageScheduler
from utils.validators import is_pinned_message, get_message_type


logger = logging.getLogger(__name__)


class MessageHandlers:
    """Handles incoming messages and schedules them for deletion."""

    def __init__(
        self,
        db: DatabaseManager,
        scheduler: MessageScheduler,
    ):
        """
        Initialize message handlers.
        
        Args:
            db: Database manager instance
            scheduler: Message scheduler instance
        """
        self.db = db
        self.scheduler = scheduler

    async def handle_text_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle text messages.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        if not update.message:
            return

        await self._process_message(update, context)

    async def handle_media_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle media messages (photos, videos, documents, etc.).
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        if not update.message:
            return

        await self._process_message(update, context)

    async def _process_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Process a message for auto-deletion.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        try:
            message = update.message
            group_id = message.chat_id

            # Ignore messages from admins and the bot itself
            if await self._should_ignore_message(update, context):
                logger.debug(f"Ignoring message {message.message_id} - admin or bot")
                return

            # Ignore pinned messages
            if is_pinned_message(message):
                logger.debug(f"Ignoring pinned message {message.message_id}")
                return

            # Get group settings
            group_settings = self.db.get_group_settings(group_id)
            if not group_settings:
                logger.debug(f"No settings found for group {group_id}, creating default")
                group_settings = self.db.get_or_create_group(group_id)

            # Check if auto-delete is enabled
            if not group_settings.auto_delete_enabled:
                logger.debug(
                    f"Auto-delete disabled for group {group_id}, ignoring message"
                )
                return

            # Track the message
            message_type = get_message_type(message)
            self.db.track_message(
                message_id=message.message_id,
                group_id=group_id,
                user_id=message.from_user.id,
                message_type=message_type,
            )

            # Schedule message deletion
            delete_after_seconds = group_settings.delete_time_minutes * 60
            success = self.scheduler.schedule_message_deletion(
                group_id=group_id,
                message_id=message.message_id,
                delete_after_seconds=delete_after_seconds,
                bot=context.bot,
            )

            if success:
                logger.info(
                    f"Scheduled deletion for message {message.message_id} "
                    f"({message_type}) in {delete_after_seconds}s"
                )
            else:
                logger.warning(
                    f"Failed to schedule deletion for message {message.message_id}"
                )

        except Exception as e:
            logger.error(
                f"Error processing message: {e}",
                exc_info=True,
            )

    async def _should_ignore_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        """
        Check if message should be ignored.
        
        Args:
            update: Telegram update object
            context: Bot context
            
        Returns:
            True if message should be ignored, False otherwise
        """
        message = update.message
        if not message or not message.from_user:
            return True

        # Ignore bot's own messages
        if message.from_user.id == context.bot.id:
            return True

        # Check if sender is admin
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=message.chat_id,
                user_id=message.from_user.id,
            )
            if chat_member.status in ["creator", "administrator"]:
                return True
        except Exception as e:
            logger.warning(f"Error checking admin status: {e}")

        return False
