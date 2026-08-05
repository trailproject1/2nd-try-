"""
User commands for the Telegram Chat Cleaner Bot.

Implements commands available to all users in the group.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from database import DatabaseManager


logger = logging.getLogger(__name__)


class UserCommands:
    """Implements user commands."""

    def __init__(self, db: DatabaseManager):
        """
        Initialize user commands.
        
        Args:
            db: Database manager instance
        """
        self.db = db

    async def show_help(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        /help or /start - Show help message with available commands.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        try:
            help_text = (
                "<b>🤖 Telegram Chat Cleaner Bot</b>\n\n"
                "<b>📋 Available Commands:</b>\n\n"
                "<b>👥 For Everyone:</b>\n"
                "/help - Show this help message\n"
                "/start - Show this help message\n\n"
                "<b>👨‍💼 Admin Only:</b>\n"
                "/clean - Delete all messages bot can delete\n"
                "/auto on - Enable auto-delete\n"
                "/auto off - Disable auto-delete\n"
                "/time &lt;minutes&gt; - Set auto-delete timer\n"
                "/status - Show current bot status\n\n"
                "<b>ℹ️ How It Works:</b>\n"
                "• When auto-delete is enabled, all messages (except from admins and pinned messages) "
                "are scheduled for deletion\n"
                "• Default timer: 10 minutes\n"
                "• Admins can change the timer using /time &lt;minutes&gt;\n"
                "• Use /clean to manually delete all messages\n\n"
                "<b>✅ Requirements:</b>\n"
                "• Bot must be admin in the group\n"
                "• Bot must have 'Delete Messages' permission\n\n"
                "<b>📌 Special Cases:</b>\n"
                "• Messages from admins are ignored\n"
                "• Pinned messages are never deleted\n"
                "• The bot's own messages are not deleted\n"
            )

            if update.message:
                await update.message.reply_text(help_text, parse_mode="HTML")
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    help_text, parse_mode="HTML"
                )

            logger.info(f"Help requested by {update.effective_user.id}")

        except Exception as e:
            logger.error(f"Error in /help command: {e}", exc_info=True)
            try:
                if update.message:
                    await update.message.reply_text(
                        "❌ An error occurred while retrieving help information."
                    )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
