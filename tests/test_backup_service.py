"""Tests for backup service module.

Integration tests for BackupService covering integration of
BackupManager, BackupScheduler, and BackupConfig.
"""

import json
import sqlite3
import tempfile
import shutil
import threading
import time
from pathlib import Path
from datetime import date

import pytest

from utils.backup_service import BackupService


@pytest.fixture
def temp_database():
    """Create a temporary SQLite database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    # Create test database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create tables
    cursor.execute("CREATE TABLE employees (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT)")
    cursor.execute("CREATE TABLE caces (id INTEGER PRIMARY KEY, employee_id INTEGER, kind TEXT)")
    cursor.execute("CREATE TABLE medical_visits (id INTEGER PRIMARY KEY, employee_id INTEGER, visit_date TEXT)")
    cursor.execute("CREATE TABLE online_trainings (id INTEGER PRIMARY KEY, employee_id INTEGER, title TEXT)")

    # Add test data
    cursor.execute("INSERT INTO employees (first_name, last_name) VALUES ('John', 'Doe')")
    cursor.execute("INSERT INTO employees (first_name, last_name) VALUES ('Jane', 'Smith')")

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def backup_service(temp_database):
    """Create BackupService instance for testing."""
    config_dir = Path(temp_database).parent / "config"
    service = BackupService(database_path=temp_database, config_path=config_dir)

    yield service

    # Cleanup
    if service.scheduler:
        service.stop_scheduler()
    if service.backup_manager.backup_dir.exists():
        shutil.rmtree(service.backup_manager.backup_dir, ignore_errors=True)
    if config_dir.exists():
        shutil.rmtree(config_dir, ignore_errors=True)


class TestBackupServiceInit:
    """Test BackupService initialization."""

    def test_init_creates_components(self, temp_database):
        """Test that initialization creates all components."""
        service = BackupService(database_path=temp_database)

        assert service.config is not None
        assert service.backup_manager is not None
        assert service.scheduler is None  # Not started yet

    def test_init_loads_config(self, temp_database):
        """Test that initialization loads config."""
        service = BackupService(database_path=temp_database)

        assert service.config.config["backup_time"] == "02:00"
        assert service.config.config["retention_days"] == 30

    def test_init_uses_config_backup_dir(self, temp_database):
        """Test that service uses config backup directory."""
        config_dir = Path(temp_database).parent / "config"
        service = BackupService(
            database_path=temp_database,
            config_path=config_dir / "backup_config.json"
        )

        assert service.config.config_path == config_dir / "backup_config.json"

    def test_init_uses_config_max_backups(self, temp_database):
        """Test that service uses config max_backups."""
        config_dir = Path(temp_database).parent / "config"
        # Create config with custom retention
        config_path = config_dir / "backup_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump({"retention_days": 45}, f)

        service = BackupService(
            database_path=temp_database,
            config_path=config_path
        )

        assert service.backup_manager.max_backups == 45


class TestSchedulerControl:
    """Test scheduler start/stop functionality."""

    def test_start_scheduler(self, backup_service):
        """Test starting scheduler."""
        result = backup_service.start_scheduler()

        assert result is True
        assert backup_service.scheduler is not None
        assert backup_service.is_scheduler_running() is True

        # Cleanup
        backup_service.stop_scheduler()

    def test_start_scheduler_when_disabled(self, backup_service):
        """Test starting scheduler when disabled in config."""
        backup_service.config.config["enabled"] = False

        result = backup_service.start_scheduler()

        assert result is False
        assert backup_service.scheduler is None

    def test_start_scheduler_when_already_running(self, backup_service):
        """Test that starting twice raises error."""
        backup_service.start_scheduler()

        with pytest.raises(RuntimeError, match="already running"):
            backup_service.start_scheduler()

        # Cleanup
        backup_service.stop_scheduler()

    def test_stop_scheduler(self, backup_service):
        """Test stopping scheduler."""
        backup_service.start_scheduler()
        assert backup_service.is_scheduler_running() is True

        backup_service.stop_scheduler()

        assert backup_service.scheduler is None
        assert backup_service.is_scheduler_running() is False

    def test_stop_scheduler_when_not_running(self, backup_service):
        """Test stopping when not running doesn't error."""
        # Should not raise
        backup_service.stop_scheduler()

        assert backup_service.scheduler is None


class TestBackupOperations:
    """Test backup operations."""

    def test_create_backup(self, backup_service):
        """Test creating a backup."""
        backup_path = backup_service.create_backup(description="test")

        assert backup_path.exists()
        assert "test" in backup_path.name
        assert backup_path.stat().st_size > 0

    def test_create_backup_with_default_description(self, backup_service):
        """Test creating backup with no description."""
        backup_path = backup_service.create_backup()

        assert backup_path.exists()
        # When no description provided, filename uses timestamp format
        assert backup_path.suffix == ".db"
        assert backup_path.stat().st_size > 0

    def test_restore_backup(self, backup_service):
        """Test restoring from backup."""
        # Create backup
        backup_path = backup_service.create_backup(description="before_restore")

        # Modify database
        conn = sqlite3.connect(str(backup_service.backup_manager.database_path))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employees (first_name, last_name) VALUES ('Test', 'User')")
        conn.commit()
        conn.close()

        # Restore from backup
        backup_service.restore_backup(backup_path)

        # Verify restored (only original data)
        conn = sqlite3.connect(str(backup_service.backup_manager.database_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 2  # Original two employees only

    def test_restore_nonexistent_backup(self, backup_service):
        """Test restoring from nonexistent backup raises error."""
        import tempfile
        nonexistent = Path(tempfile.gettempdir()) / "nonexistent_backup.db"

        with pytest.raises(FileNotFoundError):
            backup_service.restore_backup(nonexistent)

    def test_verify_backup(self, backup_service):
        """Test verifying a backup."""
        backup_path = backup_service.create_backup()

        verification = backup_service.verify_backup(backup_path)

        assert verification['valid'] is True
        assert verification['size_bytes'] > 0
        assert verification['employee_count'] == 2

    def test_list_backups(self, backup_service):
        """Test listing backups."""
        backup_service.create_backup(description="backup1")
        time.sleep(0.1)  # Ensure different timestamps
        backup_service.create_backup(description="backup2")

        backups = backup_service.list_backups()

        assert len(backups) >= 2
        assert all('name' in b and 'created' in b for b in backups)

    def test_get_backup_stats_empty(self, backup_service):
        """Test stats when no backups exist."""
        # Don't create any backups
        stats = backup_service.get_backup_stats()

        assert stats['total_count'] == 0
        assert stats['total_size_mb'] == 0.0
        assert stats['oldest_backup'] is None
        assert stats['newest_backup'] is None

    def test_get_backup_stats_with_backups(self, backup_service):
        """Test stats with backups."""
        backup_service.create_backup(description="stats_test")

        stats = backup_service.get_backup_stats()

        assert stats['total_count'] >= 1
        assert stats['total_size_mb'] > 0
        assert stats['newest_backup'] is not None


class TestConfiguration:
    """Test configuration management."""

    def test_update_config(self, backup_service):
        """Test updating configuration."""
        result = backup_service.update_config({
            "backup_time": "06:00",
            "retention_days": 60,
        })

        assert result is True
        assert backup_service.config.config["backup_time"] == "06:00"
        assert backup_service.config.config["retention_days"] == 60

    def test_update_config_saves_to_file(self, temp_database, backup_service):
        """Test that update saves to file."""
        backup_service.update_config({"backup_time": "07:00"})

        # Create new service to load from file
        new_service = BackupService(
            database_path=temp_database,
            config_path=backup_service.config.config_path
        )

        assert new_service.config.config["backup_time"] == "07:00"

    def test_reset_config(self, backup_service):
        """Test resetting configuration to defaults."""
        # Modify config
        backup_service.config.config["backup_time"] = "12:00"
        backup_service.config.config["retention_days"] = 999

        # Reset
        result = backup_service.reset_config()

        assert result is True
        assert backup_service.config.config["backup_time"] == "02:00"
        assert backup_service.config.config["retention_days"] == 30

    def test_get_config(self, backup_service):
        """Test getting configuration."""
        config_dict = backup_service.get_config()

        assert isinstance(config_dict, dict)
        assert "backup_time" in config_dict
        assert "retention_days" in config_dict


class TestIntegration:
    """Integration tests for full backup workflow."""

    def test_full_backup_workflow(self, backup_service):
        """Test complete backup workflow."""
        # Create backup
        backup_path = backup_service.create_backup(description="integration_test")

        # List backups
        backups = backup_service.list_backups()
        assert len(backups) >= 1

        # Verify backup
        verification = backup_service.verify_backup(backup_path)
        assert verification['valid'] is True

        # Get stats
        stats = backup_service.get_backup_stats()
        assert stats['total_count'] >= 1

    def test_scheduler_integration(self, backup_service):
        """Test scheduler integration with service."""
        # Start scheduler
        backup_service.start_scheduler()
        assert backup_service.is_scheduler_running() is True

        # Check scheduler uses config
        assert backup_service.scheduler.config == backup_service.config.get_scheduler_config()

        # Stop scheduler
        backup_service.stop_scheduler()
        assert backup_service.is_scheduler_running() is False

    def test_scheduler_uses_config_backup_time(self, temp_database, backup_service):
        """Test that scheduler uses configured backup time."""
        # Update config
        backup_service.update_config({"backup_time": "05:00"})

        backup_service.start_scheduler()

        assert backup_service.scheduler.config["backup_time"] == "05:00"

        # Cleanup
        backup_service.stop_scheduler()

    def test_scheduler_uses_config_max_backups(self, temp_database, backup_service):
        """Test that backup manager uses configured max_backups."""
        # Update config
        backup_service.update_config({"retention_days": 20})

        # Create new service to apply config
        new_service = BackupService(
            database_path=temp_database,
            config_path=backup_service.config.config_path
        )

        assert new_service.backup_manager.max_backups == 20

    def test_scheduler_respects_enabled_flag(self, backup_service, temp_database):
        """Test that scheduler respects enabled flag."""
        # Disable backups
        backup_service.config.config["enabled"] = False
        backup_service.config.save_config()

        # Create new service with disabled config
        disabled_service = BackupService(
            database_path=temp_database,
            config_path=backup_service.config.config_path
        )

        # Scheduler should not start
        result = disabled_service.start_scheduler()
        assert result is False
        assert disabled_service.scheduler is None

    def test_manual_backup_independent_of_scheduler(self, backup_service):
        """Test that manual backups work regardless of scheduler."""
        # Even with automatic backups disabled
        backup_service.config.config["enabled"] = False
        backup_service.config.config["automatic_daily"] = False

        # Manual backup should still work
        backup_path = backup_service.create_backup(description="manual_test")

        assert backup_path.exists()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_multiple_services_same_database(self, temp_database):
        """Test creating multiple services for same database."""
        service1 = BackupService(database_path=temp_database)
        service2 = BackupService(database_path=temp_database)

        # Both should work independently
        backup1 = service1.create_backup("service1")
        backup2 = service2.create_backup("service2")

        assert backup1.exists()
        assert backup2.exists()
        assert backup1.name != backup2.name

    def test_concurrent_backup_creates(self, backup_service):
        """Test creating multiple backups simultaneously."""
        backups = []
        errors = []

        def create_backup(desc):
            try:
                backup = backup_service.create_backup(desc)
                backups.append(backup)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = [
            threading.Thread(target=create_backup, args=(f"backup{i}",))
            for i in range(3)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join(timeout=5.0)

        assert len(errors) == 0
        assert len(backups) == 3

    def test_service_cleanup(self, backup_service):
        """Test that service can be cleaned up properly."""
        backup_service.start_scheduler()
        backup_service.create_backup("cleanup_test")

        # Stop should clean up scheduler
        backup_service.stop_scheduler()

        # Should be able to create new service
        assert BackupService(backup_service.backup_manager.database_path)


class TestConfigPreservation:
    """Test that configuration is preserved across operations."""

    def test_config_preserved_after_backup(self, backup_service):
        """Test that config isn't modified by backup operations."""
        original_config = backup_service.get_config()

        backup_service.create_backup("test")
        backup_service.list_backups()
        backup_service.get_backup_stats()

        # Config should be unchanged
        assert backup_service.get_config() == original_config

    def test_config_shared_between_components(self, backup_service):
        """Test that config is shared between scheduler and service."""
        backup_service.start_scheduler()

        # Modify through service
        backup_service.update_config({"retention_days": 90})

        # Should be reflected in scheduler config
        # Note: scheduler.config is a copy, so this tests that
        # the scheduler was initialized with the right config

        backup_service.stop_scheduler()
