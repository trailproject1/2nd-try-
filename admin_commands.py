"""
Admin commands for the Telegram Chat Cleaner Bot.

Implements commands for admins to manage bot behavior in groups.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from database import DatabaseManager
from scheduler.message_scheduler import MessageScheduler
from utils.validators import (
    is_user_admin,
    bot_can_delete_messages,
    is_valid_delete_time,
)


logger = logging.getLogger(__name__)


class AdminCommands:
    """Implements admin commands."""

    def __init__(
        self,
        db: DatabaseManager,
        scheduler: MessageScheduler,
    ):
        """
        Initialize admin commands.
        
        Args:
            db: Database manager instance
            scheduler: Message scheduler instance
        """
        self.db = db
        self.scheduler = scheduler

    async def clean_all(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        /clean - Delete all tracked messages in the group.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        if not update.message:
            return

        try:
            # Check if user is admin
            if not await is_user_admin(update, context):
                await update.message.reply_text(
                    "❌ This command is only available to group administrators."
                )
                return

            group_id = update.message.chat_id

            # Check bot permissions
            if not await bot_can_delete_messages(group_id, context):
                await update.message.reply_text(
                    "❌ I don't have permission to delete messages. "
                    "Please make sure I'm an admin with delete permission."
                )
                return

            # Get all tracked messages in the group
            tracked_messages = self.db.get_all_tracked_messages(group_id)

            if not tracked_messages:
                await update.message.reply_text("✅ No messages to clean up.")
                return

            deleted_count = 0
            failed_count = 0

            # Delete each tracked message
            for msg in tracked_messages:
                try:
                    await context.bot.delete_message(
                        chat_id=group_id,
                        message_id=msg.message_id,
                    )
                    deleted_count += 1
                    self.db.remove_tracked_message(msg.message_id, group_id)
                except Exception as e:
                    logger.warning(
                        f"Failed to delete message {msg.message_id}: {e}"
                    )
                    failed_count += 1

            # Log the command
            self.db.log_admin_command(
                group_id=group_id,
                admin_id=update.message.from_user.id,
                command=f"/clean (deleted: {deleted_count}, failed: {failed_count})",
            )

            # Send result
            response = f"🧹 Cleanup complete!\n"
            response += f"✅ Deleted: {deleted_count} message(s)\n"
            if failed_count > 0:
                response += f"⚠️ Failed: {failed_count} message(s)"

            await update.message.reply_text(response)
            logger.info(f"Manual cleanup executed in group {group_id}")

        except Exception as e:
            logger.error(f"Error in /clean command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while cleaning up messages."
            )

    async def toggle_auto_delete(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        /auto on|off - Enable or disable auto-delete.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        if not update.message:
            return

        try:
            # Check if user is admin
            if not await is_user_admin(update, context):
                await update.message.reply_text(
                    "❌ This command is only available to group administrators."
                )
                return

            group_id = update.message.chat_id

            # Get command argument
            if not context.args or len(context.args) == 0:
                await update.message.reply_text(
                    "❌ Usage: /auto on or /auto off"
                )
                return

            action = context.args[0].lower()

            if action not in ["on", "off"]:
                await update.message.reply_text(
                    "❌ Usage: /auto on or /auto off"
                )
                return

            enabled = action == "on"

            # Get or create group settings
            self.db.get_or_create_group(group_id)

            # Update settings
            success = self.db.update_auto_delete_status(group_id, enabled)

            if success:
                status = "🟢 enabled" if enabled else "🔴 disabled"
                await update.message.reply_text(
                    f"✅ Auto-delete is now {status}."
                )

                # Log the command
                self.db.log_admin_command(
                    group_id=group_id,
                    admin_id=update.message.from_user.id,
                    command=f"/auto {action}",
                )

                logger.info(f"Auto-delete set to {enabled} in group {group_id}")
            else:
                await update.message.reply_text(
                    "❌ Failed to update auto-delete status."
                )

        except Exception as e:
            logger.error(f"Error in /auto command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while processing your request."
            )

    async def set_delete_time(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        /time <minutes> - Set the auto-delete timer.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        if not update.message:
            return

        try:
            # Check if user is admin
            if not await is_user_admin(update, context):
                await update.message.reply_text(
                    "❌ This command is only available to group administrators."
                )
                return

            group_id = update.message.chat_id

            # Get command argument
            if not context.args or len(context.args) == 0:
                await update.message.reply_text(
                    "❌ Usage: /time <minutes>\nExample: /time 5"
                )
                return

            try:
                minutes = int(context.args[0])
            except ValueError:
                await update.message.reply_text(
                    "❌ Please provide a valid number of minutes.\nExample: /time 5"
                )
                return

            # Validate time
            if not is_valid_delete_time(minutes):
                await update.message.reply_text(
                    "❌ Delete time must be between 1 and 1440 minutes (24 hours)."
                )
                return

            # Get or create group settings
            self.db.get_or_create_group(group_id)

            # Update settings
            success = self.db.update_delete_time(group_id, minutes)

            if success:
                await update.message.reply_text(
                    f"✅ Auto-delete timer set to {minutes} minute(s)."
                )

                # Log the command
                self.db.log_admin_command(
                    group_id=group_id,
                    admin_id=update.message.from_user.id,
                    command=f"/time {minutes}",
                )

                logger.info(f"Delete time set to {minutes} in group {group_id}")
            else:
                await update.message.reply_text(
                    "❌ Failed to update delete time."
                )

        except Exception as e:
            logger.error(f"Error in /time command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while processing your request."
            )

    async def show_status(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        /status - Show current bot status for the group.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        if not update.message:
            return

        try:
            # Check if user is admin
            if not await is_user_admin(update, context):
                await update.message.reply_text(
                    "❌ This command is only available to group administrators."
                )
                return

            group_id = update.message.chat_id

            # Get group settings
            settings = self.db.get_group_settings(group_id)
            if not settings:
                settings = self.db.get_or_create_group(group_id)

            # Get pending jobs count
            pending_jobs = self.scheduler.get_pending_jobs_count()

            # Build status message
            auto_delete_status = "🟢 Enabled" if settings.auto_delete_enabled else "🔴 Disabled"
            response = (
                f"<b>🤖 Bot Status</b>\n\n"
                f"<b>Auto-Delete:</b> {auto_delete_status}\n"
                f"<b>Delete Timer:</b> {settings.delete_time_minutes} minute(s)\n"
                f"<b>Pending Deletions:</b> {pending_jobs}\n"
                f"<b>Group ID:</b> <code>{group_id}</code>"
            )

            await update.message.reply_text(response, parse_mode="HTML")

            logger.info(f"Status requested in group {group_id}")

        except Exception as e:
            logger.error(f"Error in /status command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while retrieving status."
            )
