"""Migration validation system.

Provides pre-migration and post-migration validation to ensure
database integrity and migration safety.
"""

from typing import List, Optional, Tuple
from pathlib import Path

from database.connection import database
from utils.logging_config import get_logger

logger = get_logger(__name__)


class MigrationValidationError(Exception):
    """Exception raised when migration validation fails."""

    def __init__(self, message: str, check_name: str = "unknown"):
        self.check_name = check_name
        super().__init__(message)


class MigrationValidator:
    """Validator for database migrations.

    Provides pre-migration and post-migration checks to ensure
    database integrity and migration safety.
    """

    def __init__(self):
        """Initialize the migration validator."""
        self.pre_checks: List[callable] = []
        self.post_checks: List[callable] = []

    def add_pre_check(self, check_func: callable) -> None:
        """Add a pre-migration validation check.

        Args:
            check_func: Function that raises MigrationValidationError if validation fails
        """
        self.pre_checks.append(check_func)

    def add_post_check(self, check_func: callable) -> None:
        """Add a post-migration validation check.

        Args:
            check_func: Function that raises MigrationValidationError if validation fails
        """
        self.post_checks.append(check_func)

    def run_pre_checks(self) -> Tuple[bool, List[str]]:
        """Run all pre-migration validation checks.

        Returns:
            Tuple of (success: bool, errors: List[str])
        """
        errors = []

        for check in self.pre_checks:
            try:
                check()
                logger.info(f"Pre-check passed: {check.__name__}")
            except MigrationValidationError as e:
                error_msg = f"Pre-check failed ({e.check_name}): {e}"
                logger.error(error_msg)
                errors.append(error_msg)
            except Exception as e:
                error_msg = f"Pre-check error ({check.__name__}): {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        return len(errors) == 0, errors

    def run_post_checks(self) -> Tuple[bool, List[str]]:
        """Run all post-migration validation checks.

        Returns:
            Tuple of (success: bool, errors: List[str])
        """
        errors = []

        for check in self.post_checks:
            try:
                check()
                logger.info(f"Post-check passed: {check.__name__}")
            except MigrationValidationError as e:
                error_msg = f"Post-check failed ({e.check_name}): {e}"
                logger.error(error_msg)
                errors.append(error_msg)
            except Exception as e:
                error_msg = f"Post-check error ({check.__name__}): {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        return len(errors) == 0, errors


# Default validator with common checks
default_validator = MigrationValidator()


def check_database_writable() -> None:
    """Check that database is writable.

    Raises:
        MigrationValidationError: If database is not writable
    """
    try:
        if database.is_closed():
            database.connect()

        # Try to create a test table
        from peewee import Model, CharField

        class TestTable(Model):
            name = CharField()

            class Meta:
                database = database
                table_name = "_migration_test_write"

        try:
            database.create_tables([TestTable], safe=True)
            TestTable.drop_table()
        except Exception as e:
            raise MigrationValidationError(
                f"Database is not writable: {e}",
                check_name="database_writable"
            )

    except MigrationValidationError:
        raise
    except Exception as e:
        raise MigrationValidationError(
            f"Failed to check database write permissions: {e}",
            check_name="database_writable"
        )


def check_disk_space(required_mb: int = 50) -> None:
    """Check that there's enough disk space for backup and migration.

    Args:
        required_mb: Required disk space in MB

    Raises:
        MigrationValidationError: If insufficient disk space
    """
    try:
        import shutil

        # Get database path
        db_path = database.database
        if db_path is None or db_path == ":memory:":
            return  # In-memory database, skip check

        db_path = Path(db_path)

        # Get disk usage
        usage = shutil.disk_usage(db_path.parent)

        # Convert to MB
        free_mb = usage.free / (1024 * 1024)

        if free_mb < required_mb:
            raise MigrationValidationError(
                f"Insufficient disk space: {free_mb:.1f}MB free, {required_mb}MB required",
                check_name="disk_space"
            )

    except MigrationValidationError:
        raise
    except Exception as e:
        raise MigrationValidationError(
            f"Failed to check disk space: {e}",
            check_name="disk_space"
        )


def check_no_active_connections() -> None:
    """Check that there are no other active connections to the database.

    Note: This is a basic check for SQLite. For other databases,
    more sophisticated connection checking may be needed.

    Raises:
        MigrationValidationError: If there may be active connections
    """
    # SQLite handles locking automatically, so this is mainly a warning
    # For production databases with multiple users, implement proper checks
    pass


def check_tables_integrity() -> None:
    """Check that existing tables have integrity.

    Raises:
        MigrationValidationError: If table integrity check fails
    """
    try:
        if database.is_closed():
            database.connect()

        # For SQLite, run PRAGMA integrity_check
        cursor = database.execute_sql("PRAGMA integrity_check")
        result = cursor.fetchone()

        if result and result[0] != "ok":
            raise MigrationValidationError(
                f"Database integrity check failed: {result[0]}",
                check_name="tables_integrity"
            )

    except MigrationValidationError:
        raise
    except Exception as e:
        # If pragma fails (e.g., on non-SQLite), log warning but don't fail
        logger.warning(f"Could not run integrity check: {e}")


def check_version_table_exists() -> None:
    """Check that version table exists or can be created.

    Raises:
        MigrationValidationError: If version table cannot be created
    """
    try:
        from database.version_model import AppVersion

        if database.is_closed():
            database.connect()

        if not AppVersion.table_exists():
            # Try to create it
            database.create_tables([AppVersion])
            logger.info("Created AppVersion table")

    except MigrationValidationError:
        raise
    except Exception as e:
        raise MigrationValidationError(
            f"Failed to check/create version table: {e}",
            check_name="version_table_exists"
        )


# Add default checks to validator
default_validator.add_pre_check(check_database_writable)
default_validator.add_pre_check(check_disk_space)
default_validator.add_pre_check(check_tables_integrity)
default_validator.add_pre_check(check_version_table_exists)


def get_validator() -> MigrationValidator:
    """Get the default migration validator.

    Returns:
        MigrationValidator instance with default checks
    """
    return default_validator


def validate_before_migration() -> Tuple[bool, List[str]]:
    """Run all pre-migration validation checks.

    Returns:
        Tuple of (success: bool, errors: List[str])
    """
    validator = get_validator()
    return validator.run_pre_checks()


def validate_after_migration() -> Tuple[bool, List[str]]:
    """Run all post-migration validation checks.

    Returns:
        Tuple of (success: bool, errors: List[str])
    """
    validator = get_validator()
    return validator.run_post_checks()
