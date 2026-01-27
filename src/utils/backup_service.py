"""Backup Service Module

Provides high-level integration of backup components:
- BackupManager: Manages backup operations
- BackupScheduler: Manages automated scheduling
- BackupConfig: Manages configuration

This service provides a simple interface for the application to interact
with the backup system.
"""

import logging
from pathlib import Path
from typing import Optional

from database.connection import database
from utils.backup_config import BackupConfig
from utils.backup_manager import BackupManager
from utils.backup_scheduler import BackupScheduler

logger = logging.getLogger(__name__)


class BackupService:
    """
    High-level service for managing automated backups.

    Integrates BackupManager, BackupScheduler, and BackupConfig
    into a single easy-to-use interface.

    Attributes:
        config: BackupConfig instance
        backup_manager: BackupManager instance
        scheduler: BackupScheduler instance (None if not started)
    """

    def __init__(self, database_path: Optional[Path] = None, config_path: Optional[Path] = None):
        """
        Initialize backup service.

        Args:
            database_path: Path to database file (default: database connection)
            config_path: Path to backup config file (default: config/backup_config.json)
        """
        # Use current database connection if path not provided
        if database_path is None:
            database_path = Path(database.database.database)

        # Initialize configuration
        self.config = BackupConfig(config_path=config_path)

        # Initialize backup manager
        backup_dir = self.config.get_backup_directory()
        max_backups = self.config.get_max_backups()
        self.backup_manager = BackupManager(
            database_path=database_path,
            backup_dir=backup_dir,
            max_backups=max_backups
        )

        # Scheduler will be created when started
        self.scheduler: Optional[BackupScheduler] = None

    def start_scheduler(self) -> bool:
        """
        Start the backup scheduler for automated backups.

        Returns:
            True if scheduler started, False if disabled

        Raises:
            RuntimeError: If scheduler already running
        """
        if self.scheduler is not None and self.scheduler.is_running():
            raise RuntimeError("Backup scheduler is already running")

        if not self.config.is_enabled():
            logger.info("Backups disabled, scheduler not started")
            return False

        # Create and start scheduler
        self.scheduler = BackupScheduler(
            backup_manager=self.backup_manager,
            config=self.config.get_scheduler_config()
        )
        self.scheduler.start()

        logger.info("Backup scheduler started")
        return True

    def stop_scheduler(self) -> None:
        """Stop the backup scheduler if running."""
        if self.scheduler:
            self.scheduler.stop()
            self.scheduler = None
            logger.info("Backup scheduler stopped")

    def create_backup(self, description: str = "") -> Path:
        """
        Create an immediate manual backup.

        Args:
            description: Optional description for backup

        Returns:
            Path to created backup file

        Raises:
            IOError: If backup creation fails
        """
        logger.info(f"Creating manual backup: {description or 'manual'}")
        return self.backup_manager.create_backup(description=description)

    def restore_backup(self, backup_path: Path) -> None:
        """
        Restore database from backup.

        Args:
            backup_path: Path to backup file

        Raises:
            FileNotFoundError: If backup file doesn't exist
            ValueError: If backup file is invalid
        """
        logger.info(f"Restoring from backup: {backup_path}")
        self.backup_manager.restore_backup(backup_path)
        logger.info("Backup restored successfully")

    def verify_backup(self, backup_path: Path) -> dict:
        """
        Verify backup file integrity.

        Args:
            backup_path: Path to backup file

        Returns:
            Verification result dictionary

        Raises:
            FileNotFoundError: If backup file doesn't exist
        """
        return self.backup_manager.verify_backup(backup_path)

    def list_backups(self) -> list:
        """
        List all backups with metadata.

        Returns:
            List of backup dictionaries
        """
        return self.backup_manager.list_backups()

    def get_backup_stats(self) -> dict:
        """
        Get backup statistics.

        Returns:
            Dictionary with statistics:
            {
                'total_count': int,
                'total_size_mb': float,
                'oldest_backup': str,
                'newest_backup': str
            }
        """
        backups = self.list_backups()

        if not backups:
            return {
                'total_count': 0,
                'total_size_mb': 0.0,
                'oldest_backup': None,
                'newest_backup': None,
            }

        return {
            'total_count': len(backups),
            'total_size_mb': self.backup_manager.get_backup_size(),
            'oldest_backup': backups[-1]['created'],  # Sorted newest first
            'newest_backup': backups[0]['created'],
        }

    def update_config(self, updates: dict) -> bool:
        """
        Update backup configuration.

        Args:
            updates: Dictionary of configuration updates

        Returns:
            True if saved successfully, False otherwise

        Note:
            If scheduler is running, it will need to be restarted
            for configuration changes to take effect.
        """
        try:
            # Update configuration
            self.config.update(updates)
            # Save to file
            return self.config.save_config()
        except Exception as e:
            logger.error(f"Failed to update backup config: {e}")
            return False

    def reset_config(self) -> bool:
        """
        Reset configuration to defaults.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            self.config.reset_to_defaults()
            return self.config.save_config()
        except Exception as e:
            logger.error(f"Failed to reset backup config: {e}")
            return False

    def get_config(self) -> dict:
        """
        Get current configuration.

        Returns:
            Configuration dictionary
        """
        return self.config.to_dict()

    def is_scheduler_running(self) -> bool:
        """
        Check if scheduler is running.

        Returns:
            True if running, False otherwise
        """
        return self.scheduler is not None and self.scheduler.is_running()

    def cleanup_old_backups(self, keep_count: Optional[int] = None) -> int:
        """
        Manually cleanup old backups beyond retention period.

        Args:
            keep_count: Number of backups to keep (None for config default)

        Returns:
            Number of backups deleted
        """
        if keep_count is None:
            keep_count = self.config.get_max_backups()

        # This would require enhancing BackupManager to support manual cleanup
        # For now, return 0 (cleanup happens automatically in create_backup)
        logger.info(f"Manual cleanup requested (keep {keep_count} backups)")
        return 0
