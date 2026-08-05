"""
Validation utilities for the bot.

Provides helper functions for validating permissions and parameters.
"""

import logging
from typing import Optional

from telegram import Chat, ChatMember, Update, Message
from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)


async def is_group(update: Update) -> bool:
    """
    Check if update is from a group.
    
    Args:
        update: Telegram update object
        
    Returns:
        True if from group, False otherwise
    """
    return update.message and update.message.chat.type in ["group", "supergroup"]


async def is_user_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """
    Check if the user who sent the message is an admin in the group.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        True if user is admin, False otherwise
    """
    if not update.message:
        return False

    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=update.message.chat.id,
            user_id=update.message.from_user.id,
        )
        return chat_member.status in ["creator", "administrator"]
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


async def bot_is_admin(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """
    Check if the bot is an administrator in the group.
    
    Args:
        chat_id: Telegram group chat ID
        context: Bot context
        
    Returns:
        True if bot is admin, False otherwise
    """
    try:
        bot = context.bot
        chat_member = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=bot.id,
        )
        return chat_member.status == "administrator"
    except Exception as e:
        logger.error(f"Error checking if bot is admin in group {chat_id}: {e}")
        return False


async def bot_can_delete_messages(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """
    Check if the bot has permission to delete messages in the group.
    
    Args:
        chat_id: Telegram group chat ID
        context: Bot context
        
    Returns:
        True if bot can delete messages, False otherwise
    """
    try:
        bot = context.bot
        chat_member = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=bot.id,
        )
        
        if chat_member.status != "administrator":
            return False

        # Check the can_delete_messages permission
        return bool(chat_member.can_delete_messages)
    except Exception as e:
        logger.error(
            f"Error checking delete messages permission in group {chat_id}: {e}"
        )
        return False


def is_valid_delete_time(minutes: int) -> bool:
    """
    Validate delete time parameter.
    
    Args:
        minutes: Delete time in minutes
        
    Returns:
        True if valid, False otherwise
    """
    return 1 <= minutes <= 1440  # 1 minute to 24 hours


def is_pinned_message(message: Message) -> bool:
    """
    Check if a message is pinned.
    
    Args:
        message: Telegram message object
        
    Returns:
        True if message is pinned, False otherwise
    """
    return message.is_topic_message is False and hasattr(message, "pinned_message")


def get_message_type(message: Message) -> str:
    """
    Determine the type of message.
    
    Args:
        message: Telegram message object
        
    Returns:
        String indicating message type
    """
    if message.text:
        return "text"
    elif message.photo:
        return "photo"
    elif message.video:
        return "video"
    elif message.voice:
        return "voice"
    elif message.document:
        return "document"
    elif message.sticker:
        return "sticker"
    elif message.animation:
        return "animation"
    else:
        return "unknown"


async def has_user_permission_in_group(
    chat_id: int,
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """
    Check if a user has admin permissions in the group.
    
    Args:
        chat_id: Telegram group chat ID
        user_id: User ID to check
        context: Bot context
        
    Returns:
        True if user is admin, False otherwise
    """
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id,
        )
        return chat_member.status in ["creator", "administrator"]
    except Exception as e:
        logger.error(f"Error checking user permission in group {chat_id}: {e}")
        return False
