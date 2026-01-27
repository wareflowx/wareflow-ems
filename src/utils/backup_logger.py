"""Backup Logger Module

Provides dedicated logging for backup operations:
- Separate log file from application logs
- Structured logging for backup events
- Backup history tracking
- Performance metrics
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class BackupEvent:
    """Represents a backup event."""
    timestamp: str
    event_type: str  # start, success, failure, verify, restore, cleanup
    backup_type: str  # manual, scheduled, shutdown
    backup_path: Optional[str] = None
    size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    status: Optional[str] = None  # success, failed, partial
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


class BackupLogger:
    """
    Dedicated logger for backup operations.

    Provides both structured logging (to JSON file) and
    human-readable logging (to text file) for backup operations.

    Attributes:
        log_dir: Directory for log files
        log_file: Path to text log file
        json_log_file: Path to JSON log file
        logger: Python logger instance
    """

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize backup logger.

        Args:
            log_dir: Directory for log files (default: logs/)
        """
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Text log file (human-readable)
        self.log_file = self.log_dir / "backup.log"
        # JSON log file (machine-readable for history/analysis)
        self.json_log_file = self.log_dir / "backup_events.jsonl"

        # Setup logger
        self.logger = logging.getLogger("backup")
        self.logger.setLevel(logging.DEBUG)

        # Remove any existing handlers to avoid conflicts between test instances
        self.logger.handlers.clear()

        # File handler for text log
        file_handler = logging.FileHandler(
            self.log_file,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Log initialization
        self.logger.info("=" * 60)
        self.logger.info("Backup logger initialized")
        self.flush()

    def log_backup_start(self, backup_type: str = "manual") -> None:
        """
        Log backup operation start.

        Args:
            backup_type: Type of backup (manual, scheduled, shutdown)
        """
        message = f"Backup started | Type: {backup_type}"
        self.logger.info(message)

        # Also log to JSON for history
        self._log_json_event(BackupEvent(
            timestamp=datetime.now().isoformat(),
            event_type="start",
            backup_type=backup_type
        ))

    def log_backup_success(
        self,
        backup_path: Path,
        duration_seconds: float,
        size_bytes: int,
        backup_type: str = "manual"
    ) -> None:
        """
        Log successful backup operation.

        Args:
            backup_path: Path to backup file
            duration_seconds: Time taken to create backup
            size_bytes: Size of backup file in bytes
            backup_type: Type of backup (manual, scheduled, shutdown)
        """
        size_mb = size_bytes / (1024 * 1024)

        message = (
            f"Backup succeeded | "
            f"Type: {backup_type} | "
            f"File: {backup_path.name} | "
            f"Size: {size_mb:.2f} MB | "
            f"Duration: {duration_seconds:.2f}s"
        )
        self.logger.info(message)

        # Log to JSON for history
        self._log_json_event(BackupEvent(
            timestamp=datetime.now().isoformat(),
            event_type="success",
            backup_type=backup_type,
            backup_path=str(backup_path),
            size_bytes=size_bytes,
            duration_seconds=duration_seconds,
            status="success"
        ))

    def log_backup_failure(
        self,
        error: str,
        backup_type: str = "manual",
        backup_path: Optional[Path] = None
    ) -> None:
        """
        Log failed backup operation.

        Args:
            error: Error message
            backup_type: Type of backup (manual, scheduled, shutdown)
            backup_path: Optional path to backup file
        """
        message = f"Backup failed | Type: {backup_type} | Error: {error}"
        self.logger.error(message)

        # Log to JSON for history
        self._log_json_event(BackupEvent(
            timestamp=datetime.now().isoformat(),
            event_type="failure",
            backup_type=backup_type,
            backup_path=str(backup_path) if backup_path else None,
            status="failed",
            error_message=error
        ))

    def log_backup_verify(
        self,
        backup_path: Path,
        valid: bool,
        employee_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log backup verification result.

        Args:
            backup_path: Path to backup file
            valid: Whether backup is valid
            employee_count: Number of employees in backup
            error_message: Error message if verification failed
        """
        if valid:
            message = f"Backup verified | File: {backup_path.name} | Valid: Yes"
            if employee_count is not None:
                message += f" | Employees: {employee_count}"
            self.logger.info(message)
        else:
            message = f"Backup verification failed | File: {backup_path.name}"
            if error_message:
                message += f" | Error: {error_message}"
            self.logger.error(message)

        # Log to JSON for history
        self._log_json_event(BackupEvent(
            timestamp=datetime.now().isoformat(),
            event_type="verify",
            backup_type="manual",
            backup_path=str(backup_path),
            status="valid" if valid else "invalid",
            metadata={
                "employee_count": employee_count,
                "error_message": error_message
            } if not valid else {"employee_count": employee_count}
        ))

    def log_backup_restore(
        self,
        backup_path: Path,
        success: bool,
        duration_seconds: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log backup restore operation.

        Args:
            backup_path: Path to backup file
            success: Whether restore succeeded
            duration_seconds: Time taken to restore
            error_message: Error message if restore failed
        """
        if success:
            message = f"Restore succeeded | File: {backup_path.name}"
            if duration_seconds:
                message += f" | Duration: {duration_seconds:.2f}s"
            self.logger.info(message)
        else:
            message = f"Restore failed | File: {backup_path.name}"
            if error_message:
                message += f" | Error: {error_message}"
            self.logger.error(message)

        # Log to JSON for history
        self._log_json_event(BackupEvent(
            timestamp=datetime.now().isoformat(),
            event_type="restore",
            backup_type="manual",
            backup_path=str(backup_path),
            duration_seconds=duration_seconds,
            status="success" if success else "failed",
            error_message=error_message if not success else None
        ))

    def log_backup_cleanup(
        self,
        deleted_count: int,
        kept_count: int,
        retention_days: int
    ) -> None:
        """
        Log backup cleanup/rotation operation.

        Args:
            deleted_count: Number of backups deleted
            kept_count: Number of backups kept
            retention_days: Retention period in days
        """
        message = (
            f"Backup cleanup | "
            f"Deleted: {deleted_count} | "
            f"Kept: {kept_count} | "
            f"Retention: {retention_days} days"
        )
        self.logger.info(message)

        # Log to JSON for history
        self._log_json_event(BackupEvent(
            timestamp=datetime.now().isoformat(),
            event_type="cleanup",
            backup_type="automatic",
            metadata={
                "deleted_count": deleted_count,
                "kept_count": kept_count,
                "retention_days": retention_days
            }
        ))

    def log_scheduler_start(self) -> None:
        """Log scheduler start."""
        self.logger.info("Scheduler started")

    def log_scheduler_stop(self) -> None:
        """Log scheduler stop."""
        self.logger.info("Scheduler stopped")

    def log_scheduler_skipped(self, reason: str) -> None:
        """
        Log when scheduler skips a backup.

        Args:
            reason: Reason for skipping
        """
        message = f"Scheduled backup skipped | Reason: {reason}"
        self.logger.info(message)

    def _log_json_event(self, event: BackupEvent) -> None:
        """
        Log event to JSON log file.

        Args:
            event: Backup event to log
        """
        try:
            with open(self.json_log_file, "a", encoding="utf-8") as f:
                json.dump(asdict(event), f, ensure_ascii=False)
                f.write("\n")
        except (OSError, IOError) as e:
            # Don't fail logging if JSON log fails
            self.logger.warning(f"Failed to write JSON log: {e}")

    def get_recent_events(self, count: int = 50) -> list[dict]:
        """
        Get recent backup events from JSON log.

        Args:
            count: Maximum number of events to return

        Returns:
            List of recent events (most recent first)
        """
        if not self.json_log_file.exists():
            return []

        events = []
        try:
            with open(self.json_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        events.append(event)
                    except json.JSONDecodeError:
                        continue

            # Return most recent first
            return events[-count:][::-1]

        except (OSError, IOError):
            return []

    def get_statistics(self) -> dict:
        """
        Get backup statistics from logs.

        Returns:
            Dictionary with statistics:
            {
                'total_backups': int,
                'successful_backups': int,
                'failed_backups': int,
                'last_backup': str or None,
                'last_successful_backup': str or None,
                'average_duration_seconds': float,
                'total_size_mb': float
            }
        """
        events = self.get_recent_events(count=1000)  # Get lots of events

        stats = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'last_backup': None,
            'last_successful_backup': None,
            'average_duration_seconds': 0.0,
            'total_size_mb': 0.0
        }

        durations = []
        sizes = []

        for event in events:
            event_type = event.get('event_type')

            if event_type == 'success':
                stats['total_backups'] += 1
                stats['successful_backups'] += 1

                if not stats['last_backup']:
                    stats['last_backup'] = event['timestamp']
                    stats['last_successful_backup'] = event['timestamp']

                # Track duration
                if event.get('duration_seconds'):
                    durations.append(event['duration_seconds'])

                # Track size
                if event.get('size_bytes'):
                    sizes.append(event['size_bytes'])

            elif event_type == 'failure':
                stats['total_backups'] += 1
                stats['failed_backups'] += 1

                if not stats['last_backup']:
                    stats['last_backup'] = event['timestamp']

        # Calculate averages
        if durations:
            stats['average_duration_seconds'] = sum(durations) / len(durations)

        if sizes:
            stats['total_size_mb'] = sum(sizes) / (1024 * 1024)

        return stats

    def flush(self) -> None:
        """Flush all log handlers to ensure data is written."""
        for handler in self.logger.handlers:
            handler.flush()

    def clear_logs(self) -> None:
        """Clear all log files."""
        try:
            # Close and remove all handlers to release file handles
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)

            # Now we can delete the files
            if self.log_file.exists():
                self.log_file.unlink()

            if self.json_log_file.exists():
                self.json_log_file.unlink()

            # Recreate handler for future logging
            file_handler = logging.FileHandler(
                self.log_file,
                encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # Log that files were cleared
            self.logger.info("Log files cleared")
            self.flush()
        except (OSError, IOError) as e:
            self.logger.error(f"Failed to clear log files: {e}")
