"""
Main entry point for Telegram Chat Cleaner Bot.

This module initializes the bot, sets up handlers, and runs the application.
"""

import logging
from contextlib import asynccontextmanager

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)

from config import Config
from database import DatabaseManager
from utils.logger import setup_logging
from handlers.message_handler import MessageHandlers
from handlers.group_handler import GroupHandlers
from handlers.error_handler import ErrorHandlers
from commands.admin_commands import AdminCommands
from commands.user_commands import UserCommands
from scheduler.message_scheduler import MessageScheduler


logger = logging.getLogger(__name__)


class TelegramChatCleanerBot:
    """Main bot class responsible for initialization and lifecycle management."""

    def __init__(self):
        """Initialize the bot with configuration and database."""
        self.config = Config()
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        self.scheduler = MessageScheduler()
        
        # Initialize handlers
        self.message_handlers = MessageHandlers(self.db, self.scheduler)
        self.group_handlers = GroupHandlers(self.db)
        self.error_handlers = ErrorHandlers()
        self.admin_commands = AdminCommands(self.db, self.scheduler)
        self.user_commands = UserCommands(self.db)

    async def post_init(self, application: Application) -> None:
        """Called after the application is initialized. Set up APScheduler."""
        logger.info("Post-initialization: Starting APScheduler")
        self.scheduler.start()

    async def post_stop(self, application: Application) -> None:
        """Called when the application is shutting down. Clean up resources."""
        logger.info("Post-stop: Shutting down APScheduler")
        self.scheduler.shutdown()
        self.db.close()

    def setup_handlers(self, application: Application) -> None:
        """Register all handlers with the application."""
        # Message handlers
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.Group,
                self.message_handlers.handle_text_message,
            )
        )
        
        application.add_handler(
            MessageHandler(
                (filters.PHOTO | filters.VIDEO | filters.VOICE | 
                 filters.DOCUMENT | filters.Sticker.ALL | filters.ANIMATION) & 
                filters.Group,
                self.message_handlers.handle_media_message,
            )
        )

        # Group member status changes
        application.add_handler(
            ChatMemberHandler(
                self.group_handlers.handle_my_chat_member,
                ChatMemberHandler.MY_CHAT_MEMBER,
            )
        )

        # Admin commands
        application.add_handler(
            CommandHandler("clean", self.admin_commands.clean_all)
        )
        application.add_handler(
            CommandHandler("auto", self.admin_commands.toggle_auto_delete)
        )
        application.add_handler(
            CommandHandler("time", self.admin_commands.set_delete_time)
        )
        application.add_handler(
            CommandHandler("status", self.admin_commands.show_status)
        )

        # User commands
        application.add_handler(
            CommandHandler("help", self.user_commands.show_help)
        )
        application.add_handler(
            CommandHandler("start", self.user_commands.show_help)
        )

        # Error handler (must be last)
        application.add_error_handler(self.error_handlers.error_handler)

        logger.info("All handlers registered successfully")

    def build_app(self) -> Application:
        """Build and configure the Telegram bot application."""
        logger.info("Building Telegram bot application")
        
        application = (
            Application.builder()
            .token(self.config.BOT_TOKEN)
            .concurrent_updates(True)
            .post_init(self.post_init)
            .post_stop(self.post_stop)
            .build()
        )

        self.setup_handlers(application)
        return application


async def main() -> None:
    """Main entry point. Initialize and run the bot."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Starting Telegram Chat Cleaner Bot")
    logger.info("=" * 60)
    
    bot = TelegramChatCleanerBot()
    app = bot.build_app()
    
    logger.info(f"Bot initialized with token: {bot.config.BOT_TOKEN[:10]}...")
    logger.info(f"Database: {bot.config.DATABASE_PATH}")
    logger.info(f"Log level: {bot.config.LOG_LEVEL}")
    
    await app.run_polling(
        allowed_updates=["message", "chat_member", "my_chat_member"],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise
