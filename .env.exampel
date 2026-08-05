"""
Database management for Telegram Chat Cleaner Bot.

Handles all SQLite operations for group settings and message tracking.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class GroupSettings:
    """Data class for group settings."""
    group_id: int
    auto_delete_enabled: bool
    delete_time_minutes: int
    created_at: str
    updated_at: str


@dataclass
class TrackedMessage:
    """Data class for tracked message."""
    message_id: int
    group_id: int
    user_id: int
    message_type: str
    created_at: str


class DatabaseManager:
    """Manages all database operations using SQLite."""

    def __init__(self, db_path: str = "data/bot.db"):
        """
        Initialize database connection and create tables if needed.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info(f"Database initialized: {db_path}")

    def _ensure_db_dir(self) -> None:
        """Ensure database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _create_tables(self) -> None:
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()

        # Group settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                group_id INTEGER PRIMARY KEY,
                auto_delete_enabled BOOLEAN DEFAULT 1,
                delete_time_minutes INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tracked messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_messages (
                message_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (message_id, group_id),
                FOREIGN KEY (group_id) REFERENCES group_settings(group_id)
            )
        """)

        # Admin commands log table (optional, for audit trail)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                admin_id INTEGER NOT NULL,
                command TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES group_settings(group_id)
            )
        """)

        self.conn.commit()
        logger.debug("Database tables created/verified")

    def get_or_create_group(
        self,
        group_id: int,
        auto_delete_enabled: bool = True,
        delete_time_minutes: int = 10,
    ) -> GroupSettings:
        """
        Get or create group settings.
        
        Args:
            group_id: The Telegram group ID
            auto_delete_enabled: Whether auto-delete is enabled
            delete_time_minutes: Delete timer in minutes
            
        Returns:
            GroupSettings object
        """
        cursor = self.conn.cursor()

        # Check if group exists
        cursor.execute("SELECT * FROM group_settings WHERE group_id = ?", (group_id,))
        row = cursor.fetchone()

        if row:
            return GroupSettings(
                group_id=row["group_id"],
                auto_delete_enabled=bool(row["auto_delete_enabled"]),
                delete_time_minutes=row["delete_time_minutes"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        # Create new group settings
        cursor.execute(
            """
            INSERT INTO group_settings 
            (group_id, auto_delete_enabled, delete_time_minutes)
            VALUES (?, ?, ?)
            """,
            (group_id, auto_delete_enabled, delete_time_minutes),
        )
        self.conn.commit()
        logger.info(f"Created settings for group {group_id}")

        return GroupSettings(
            group_id=group_id,
            auto_delete_enabled=auto_delete_enabled,
            delete_time_minutes=delete_time_minutes,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def get_group_settings(self, group_id: int) -> Optional[GroupSettings]:
        """
        Retrieve group settings.
        
        Args:
            group_id: The Telegram group ID
            
        Returns:
            GroupSettings object or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM group_settings WHERE group_id = ?", (group_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return GroupSettings(
            group_id=row["group_id"],
            auto_delete_enabled=bool(row["auto_delete_enabled"]),
            delete_time_minutes=row["delete_time_minutes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def update_auto_delete_status(self, group_id: int, enabled: bool) -> bool:
        """
        Update auto-delete status for a group.
        
        Args:
            group_id: The Telegram group ID
            enabled: Whether to enable or disable auto-delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE group_settings 
                SET auto_delete_enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE group_id = ?
                """,
                (enabled, group_id),
            )
            self.conn.commit()
            logger.info(f"Auto-delete for group {group_id} set to {enabled}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error updating auto-delete: {e}")
            return False

    def update_delete_time(self, group_id: int, minutes: int) -> bool:
        """
        Update delete timer for a group.
        
        Args:
            group_id: The Telegram group ID
            minutes: Delete timer in minutes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE group_settings 
                SET delete_time_minutes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE group_id = ?
                """,
                (minutes, group_id),
            )
            self.conn.commit()
            logger.info(f"Delete time for group {group_id} set to {minutes} minutes")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error updating delete time: {e}")
            return False

    def track_message(
        self,
        message_id: int,
        group_id: int,
        user_id: int,
        message_type: str,
    ) -> bool:
        """
        Track a message for potential deletion.
        
        Args:
            message_id: The Telegram message ID
            group_id: The Telegram group ID
            user_id: The user ID who sent the message
            message_type: Type of message (text, photo, video, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO tracked_messages 
                (message_id, group_id, user_id, message_type)
                VALUES (?, ?, ?, ?)
                """,
                (message_id, group_id, user_id, message_type),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Message already tracked
            logger.debug(f"Message {message_id} already tracked in group {group_id}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error tracking message: {e}")
            return False

    def get_tracked_message(
        self, message_id: int, group_id: int
    ) -> Optional[TrackedMessage]:
        """
        Retrieve tracked message information.
        
        Args:
            message_id: The Telegram message ID
            group_id: The Telegram group ID
            
        Returns:
            TrackedMessage object or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM tracked_messages 
            WHERE message_id = ? AND group_id = ?
            """,
            (message_id, group_id),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return TrackedMessage(
            message_id=row["message_id"],
            group_id=row["group_id"],
            user_id=row["user_id"],
            message_type=row["message_type"],
            created_at=row["created_at"],
        )

    def remove_tracked_message(self, message_id: int, group_id: int) -> bool:
        """
        Remove a tracked message after deletion.
        
        Args:
            message_id: The Telegram message ID
            group_id: The Telegram group ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                DELETE FROM tracked_messages 
                WHERE message_id = ? AND group_id = ?
                """,
                (message_id, group_id),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error removing tracked message: {e}")
            return False

    def get_all_tracked_messages(self, group_id: int) -> List[TrackedMessage]:
        """
        Get all tracked messages in a group.
        
        Args:
            group_id: The Telegram group ID
            
        Returns:
            List of TrackedMessage objects
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM tracked_messages 
            WHERE group_id = ?
            """,
            (group_id,),
        )
        rows = cursor.fetchall()

        return [
            TrackedMessage(
                message_id=row["message_id"],
                group_id=row["group_id"],
                user_id=row["user_id"],
                message_type=row["message_type"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def log_admin_command(
        self, group_id: int, admin_id: int, command: str
    ) -> bool:
        """
        Log an admin command for audit trail.
        
        Args:
            group_id: The Telegram group ID
            admin_id: The admin user ID
            command: The command executed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO admin_logs (group_id, admin_id, command)
                VALUES (?, ?, ?)
                """,
                (group_id, admin_id, command),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error logging admin command: {e}")
            return False

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __del__(self) -> None:
        """Ensure database is closed on object deletion."""
        self.close()
