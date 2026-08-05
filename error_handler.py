"""
Error handlers for graceful error handling.

Logs errors and prevents the bot from crashing.
"""

import logging
import traceback

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest, Forbidden


logger = logging.getLogger(__name__)


class ErrorHandlers:
    """Handles errors gracefully."""

    async def error_handler(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle errors in the bot.
        
        Args:
            update: Telegram update object
            context: Bot context with the error
        """
        error = context.error
        
        logger.error(f"Exception while handling an update: {error}")
        logger.error(traceback.format_exc())

        # Extract info from update if available
        update_info = ""
        if update:
            if update.message:
                update_info = (
                    f"Message: {update.message.text[:50] if update.message.text else 'media'} "
                    f"from user {update.message.from_user.id} "
                    f"in chat {update.message.chat_id}"
                )
            elif update.callback_query:
                update_info = f"Callback: {update.callback_query.data}"

        # Handle specific error types
        if isinstance(error, Forbidden):
            logger.warning(
                f"Forbidden error (likely bot removed from group): {error}. {update_info}"
            )
        elif isinstance(error, BadRequest):
            logger.warning(f"Bad request: {error}. {update_info}")
        elif isinstance(error, TelegramError):
            logger.warning(f"Telegram error: {error}. {update_info}")
        else:
            logger.error(f"Unexpected error type: {type(error).__name__}: {error}")

        # Attempt to notify user/group of the error if safe to do so
        try:
            if update and update.message and update.message.chat_id:
                # Only send error message for user errors, not system errors
                if isinstance(error, (BadRequest, Forbidden)):
                    await context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text=(
                            "⚠️ An error occurred while processing your request. "
                            "The issue has been logged and will be reviewed."
                        ),
                    )
        except Exception as send_error:
            logger.error(f"Failed to send error notification: {send_error}")

    @staticmethod
    def handle_sync_errors(exception: Exception) -> None:
        """
        Handle synchronous errors (outside of async handlers).
        
        Args:
            exception: The exception that occurred
        """
        logger.critical(f"Critical error: {exception}", exc_info=True)
        raise exception
