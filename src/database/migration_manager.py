"""Automatic migration manager for database schema upgrades.

This module handles automatic database migrations on application startup,
ensuring the database schema is always up to date with the application version.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from database.connection import database
from database.migrations import get_pending_migrations
from database.migration_model import get_applied_migrations, get_last_batch_number
from database.version import check_migration_needed, initialize_version_tracking
from database.version_model import AppVersion, get_current_app_version, set_version
from database.version import APP_VERSION, SCHEMA_VERSION
from employee.models import Caces, Employee, MedicalVisit, OnlineTraining
from lock.models import AppLock
from utils.backup_manager import BackupManager
from utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=True)
logger = get_logger(__name__)


class MigrationManager:
    """Manager for automatic database migrations."""

    def __init__(self, backup_manager: Optional[BackupManager] = None):
        """Initialize the migration manager.

        Args:
            backup_manager: Optional backup manager for creating pre-migration backups
        """
        self.backup_manager = backup_manager or BackupManager()
        self.migrations_dir = Path(__file__).parent.parent.parent / "database" / "migrations"

    def check_and_migrate(self, auto_migrate: bool = False) -> Tuple[bool, str]:
        """Check if migration is needed and optionally perform it.

        Args:
            auto_migrate: If True, automatically perform migrations

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Initialize version tracking
            initialize_version_tracking()

            # Check if migration is needed
            if not check_migration_needed():
                return True, "Database is up to date"

            # Get pending migrations
            pending = self._get_pending_migrations()
            if not pending:
                # No migrations needed even though version changed
                # Just update version
                self._update_version_record()
                return True, "Version updated (no schema changes)"

            logger.info(f"Migration needed: {len(pending)} migration(s) pending")

            if not auto_migrate:
                return False, f"Migration required: {len(pending)} migration(s) pending"

            # Perform automatic migration
            return self._perform_migration(pending)

        except Exception as e:
            error_msg = f"Migration check failed: {e}"
            logger.error(error_msg)
            return False, error_msg

    def _get_pending_migrations(self) -> List:
        """Get list of pending migration instances.

        Returns:
            List of migration instances to apply
        """
        try:
            return get_pending_migrations(self.migrations_dir)
        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []

    def _perform_migration(self, pending_migrations: List) -> Tuple[bool, str]:
        """Perform database migration with safety measures.

        Args:
            pending_migrations: List of migration instances to apply

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create backup before migration
            logger.info("Creating pre-migration backup...")
            backup_path = self.backup_manager.create_backup("pre_migration")
            logger.info(f"Backup created: {backup_path.name}")

            # Get next batch number
            batch = get_last_batch_number() + 1

            # Apply migrations sequentially
            for i, migration in enumerate(pending_migrations, 1):
                migration_name = migration.name if hasattr(migration, 'name') else f"migration_{i}"
                logger.info(f"Applying migration {i}/{len(pending_migrations)}: {migration_name}")

                # Pre-check
                if hasattr(migration, 'pre_check') and not migration.pre_check():
                    error_msg = f"Migration pre-check failed: {migration_name}"
                    logger.error(error_msg)
                    return False, error_msg

                # Apply migration
                if not self._apply_single_migration(migration, batch):
                    error_msg = f"Migration failed: {migration_name}"
                    logger.error(error_msg)
                    return False, error_msg

                # Post-check
                if hasattr(migration, 'post_check') and not migration.post_check():
                    error_msg = f"Migration post-check failed: {migration_name}"
                    logger.error(error_msg)
                    return False, error_msg

                # Record migration
                from database.migration_model import record_migration
                migration_name = migration.name if hasattr(migration, 'name') else f"migration_{i}"
                record_migration(migration_name, batch)

                logger.info(f"Migration {i}/{len(pending_migrations)} completed: {migration_name}")

            # Update version record after all migrations succeed
            self._update_version_record()

            success_msg = f"Successfully applied {len(pending_migrations)} migration(s)"
            logger.info(success_msg)

            return True, success_msg

        except Exception as e:
            error_msg = f"Migration failed: {e}"
            logger.error(error_msg)
            return False, error_msg

    def _apply_single_migration(self, migration, batch: int) -> bool:
        """Apply a single migration.

        Args:
            migration: Migration instance to apply
            batch: Batch number for this migration run

        Returns:
            True if migration succeeded, False otherwise
        """
        try:
            # Import migration run function
            from database.migrations import run_migration

            # Run migration
            success = run_migration(migration, batch)
            return success

        except Exception as e:
            logger.error(f"Failed to apply migration: {e}")
            return False

    def _update_version_record(self) -> None:
        """Update the version record in database after successful migration."""
        try:
            if database.is_closed():
                database.connect()

            # Update version to current
            current = get_current_app_version()
            if current != APP_VERSION:
                set_version(APP_VERSION, SCHEMA_VERSION, f"Upgrade to {APP_VERSION}")
                logger.info(f"Version updated: {current} -> {APP_VERSION}")
            else:
                # Just update timestamp to mark migration complete
                from database.migration_model import Migration, get_last_batch_number
                if Migration.select().count() > 0:
                    batch = get_last_batch_number()
                    # Update the most recent migration's timestamp
                    migrations = Migration.select().where(Migration.batch == batch)
                    for m in migrations:
                        m.applied_at = datetime.now()
                        m.save()

        except Exception as e:
            logger.error(f"Failed to update version record: {e}")

    def get_migration_plan(self) -> dict:
        """Get a preview of the migration plan without executing it.

        Returns:
            Dictionary with migration plan details
        """
        try:
            initialize_version_tracking()

            pending = self._get_pending_migrations()

            plan = {
                "current_version": get_current_app_version() or "unknown",
                "target_version": APP_VERSION,
                "pending_count": len(pending),
                "migrations": []
            }

            for migration in pending:
                migration_name = migration.name if hasattr(migration, 'name') else "Unknown"
                plan["migrations"].append(migration_name)

            return plan

        except Exception as e:
            logger.error(f"Failed to get migration plan: {e}")
            return {
                "current_version": "unknown",
                "target_version": APP_VERSION,
                "pending_count": 0,
                "migrations": [],
                "error": str(e)
            }


def get_migration_manager(backup_manager: Optional[BackupManager] = None) -> MigrationManager:
    """Get the migration manager singleton instance.

    Args:
        backup_manager: Optional backup manager

    Returns:
        MigrationManager instance
    """
    # For now, create a new instance each time
    # TODO: Make this a true singleton if needed
    return MigrationManager(backup_manager)
