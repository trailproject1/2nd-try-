"""
Group handlers for managing bot status and permissions in groups.

Handles bot joining/leaving groups and permission validation.
"""

import logging

from telegram import Update, ChatMember
from telegram.ext import ContextTypes

from database import DatabaseManager
from utils.validators import bot_is_admin, bot_can_delete_messages


logger = logging.getLogger(__name__)


class GroupHandlers:
    """Handles group membership and status changes."""

    def __init__(self, db: DatabaseManager):
        """
        Initialize group handlers.
        
        Args:
            db: Database manager instance
        """
        self.db = db

    async def handle_my_chat_member(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle bot's chat member status changes (added to group, removed, etc.).
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        try:
            chat_member_update = update.my_chat_member
            if not chat_member_update:
                return

            chat = chat_member_update.chat
            new_member: ChatMember = chat_member_update.new_chat_member
            old_member: ChatMember = chat_member_update.old_chat_member

            # Bot was added to a group
            if old_member.status == "left" and new_member.status != "left":
                await self._handle_bot_added(chat.id, context)

            # Bot was removed from a group
            elif old_member.status != "left" and new_member.status == "left":
                await self._handle_bot_removed(chat.id)

            # Bot's permissions were updated
            elif new_member.status == "administrator":
                await self._handle_permissions_update(chat.id, new_member, context)

        except Exception as e:
            logger.error(
                f"Error handling chat member update: {e}",
                exc_info=True,
            )

    async def _handle_bot_added(
        self,
        group_id: int,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle bot being added to a group.
        
        Args:
            group_id: The group ID
            context: Bot context
        """
        logger.info(f"Bot added to group {group_id}")

        try:
            # Create group settings in database
            self.db.get_or_create_group(group_id)

            # Check if bot is admin
            is_admin = await bot_is_admin(group_id, context)
            if not is_admin:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=(
                        "⚠️ <b>Permission Warning</b>\n\n"
                        "I need to be an administrator in this group to function properly. "
                        "Please promote me to administrator so I can delete messages.\n\n"
                        "Use /help for available commands."
                    ),
                    parse_mode="HTML",
                )
                logger.warning(f"Bot is not admin in group {group_id}")
                return

            # Check if bot can delete messages
            can_delete = await bot_can_delete_messages(group_id, context)
            if not can_delete:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=(
                        "⚠️ <b>Permission Warning</b>\n\n"
                        "I am an administrator but don't have the "
                        "<b>Delete Messages</b> permission. "
                        "Please grant this permission for me to work properly.\n\n"
                        "Use /help for available commands."
                    ),
                    parse_mode="HTML",
                )
                logger.warning(
                    f"Bot doesn't have delete permission in group {group_id}"
                )
                return

            # All permissions OK
            await context.bot.send_message(
                chat_id=group_id,
                text=(
                    "✅ <b>Setup Complete</b>\n\n"
                    "I'm ready to clean up messages! "
                    "By default, I will automatically delete messages after 10 minutes.\n\n"
                    "Use /help to see all available commands."
                ),
                parse_mode="HTML",
            )
            logger.info(f"Bot successfully set up in group {group_id}")

        except Exception as e:
            logger.error(f"Error handling bot addition to group {group_id}: {e}")

    async def _handle_bot_removed(self, group_id: int) -> None:
        """
        Handle bot being removed from a group.
        
        Args:
            group_id: The group ID
        """
        logger.info(f"Bot removed from group {group_id}")
        # Note: We keep the group settings in database in case bot is re-added

    async def _handle_permissions_update(
        self,
        group_id: int,
        chat_member: ChatMember,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle bot's permissions being updated.
        
        Args:
            group_id: The group ID
            chat_member: The updated chat member info
            context: Bot context
        """
        logger.info(f"Bot permissions updated in group {group_id}")

        try:
            # Check if bot still has delete permission
            if not chat_member.can_delete_messages:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=(
                        "⚠️ <b>Permission Lost</b>\n\n"
                        "My <b>Delete Messages</b> permission has been revoked. "
                        "I won't be able to clean up messages without this permission."
                    ),
                    parse_mode="HTML",
                )
                logger.warning(
                    f"Bot lost delete permission in group {group_id}"
                )
                return

            logger.info(f"Bot has all required permissions in group {group_id}")

        except Exception as e:
            logger.error(f"Error handling permissions update in group {group_id}: {e}")
