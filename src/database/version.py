"""Application version tracking and management.

This module provides centralized version management for the application,
ensuring a single source of truth for version information.
"""

from pathlib import Path

from database.connection import database
from database.version_model import AppVersion, get_current_app_version, set_version


# Current application version
APP_VERSION = "0.1.0"
SCHEMA_VERSION = 1

# Version metadata
VERSION_INFO = {
    "app_version": APP_VERSION,
    "schema_version": SCHEMA_VERSION,
    "display_name": f"v{APP_VERSION}",
}


def get_app_version() -> str:
    """Get the current application version.

    Returns:
        Application version string
    """
    return APP_VERSION


def get_schema_version() -> int:
    """Get the current database schema version.

    Returns:
        Schema version number
    """
    return SCHEMA_VERSION


def initialize_version_tracking() -> None:
    """Initialize version tracking in the database.

    Creates or updates the app_version table with current version.
    """
    try:
        if database.is_closed():
            database.connect()

        # Create table if not exists
        if not AppVersion.table_exists():
            database.create_tables([AppVersion])

        # Check if we need to set initial version
        current = get_current_app_version()
        if current != APP_VERSION:
            # Update version
            set_version(APP_VERSION, SCHEMA_VERSION, f"Initial version {APP_VERSION}")
            print(f"[OK] Version tracking initialized: {APP_VERSION}")

    except Exception as e:
        print(f"[WARN] Failed to initialize version tracking: {e}")


def check_migration_needed() -> bool:
    """Check if database migration is needed.

    Returns:
        True if migration is needed, False otherwise
    """
    try:
        if database.is_closed():
            database.connect()

        # If no version table exists, migration is needed
        if not AppVersion.table_exists():
            return True

        # Check if current version matches
        current = get_current_app_version()
        return current != APP_VERSION

    except Exception:
        # If we can't check, assume migration is needed
        return True
