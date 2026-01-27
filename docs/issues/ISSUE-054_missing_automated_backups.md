# ISSUE-054: Missing Automated Backup System

## Description

The backup system only supports manual backups (40% complete). Critical automated backup features are missing: automatic daily backups, backup rotation, and scheduled backups. This puts production data at risk.

## Affected Files

- **`src/utils/backup_manager.py`** - Backup logic (partial)
- **`src/ui_ctk/views/backup_view.py`** - Backup UI (partial)
- **`src/utils/config.py`** - Configuration management

## Current State

### What Works:
- Manual backup creation
- Manual backup restore
- Basic UI for backup operations
- File compression

### What's Missing:
1. **Automatic Daily Backups** - No scheduled backups
2. **Backup Rotation** - No automatic cleanup of old backups
3. **Backup Verification** - No verification that backups are valid
4. **Backup Retention Policy** - No configurable retention (keep last N days)
5. **Backup Notifications** - No success/failure notifications
6. **Incremental Backups** - Only full backups supported
7. **Backup Scheduling** - No scheduling interface
8. **Backup Logging** - No comprehensive backup logs
9. **Cloud Storage** - No cloud backup support
10. **Backup Testing** - No automatic restore testing

## Expected Behavior

### 1. Automatic Daily Backups

**Requirements:**
- Automatic backup at configurable time (default: 2:00 AM)
- Backup on application shutdown (optional)
- Backup before database migrations (automatic)
- Backup before critical operations (configurable)

**Configuration:**
```json
{
  "backup": {
    "enabled": true,
    "automatic_daily": true,
    "backup_time": "02:00",
    "backup_on_shutdown": true,
    "backup_directory": "./backups",
    "retention_days": 30
  }
}
```

### 2. Backup Rotation

**Requirements:**
- Keep last N days of daily backups (configurable, default: 30)
- Keep last N weeks of weekly backups (configurable, default: 12)
- Keep last N months of monthly backups (configurable, default: 12)
- Automatic cleanup of old backups
- Manual backups never deleted automatically

**Algorithm:**
```python
def rotate_backups():
    """Rotate backups according to retention policy."""
    # Keep daily backups for retention_days
    # Keep weekly backups (one per week)
    # Keep monthly backups (one per month)
    # Delete backups older than policy
    # Never delete manual backups
```

### 3. Backup Verification

**Requirements:**
- Verify backup file integrity after creation
- Test restore on random backup (weekly)
- Verify backup file size (not too small)
- Verify database can be opened from backup
- Log verification results

### 4. Backup Logging

**Requirements:**
- Log all backup operations (start, success, failure)
- Log backup file size and duration
- Log backup verification results
- Log cleanup operations
- Keep backup log separate from application log

### 5. Backup UI Enhancements

**Add to `src/ui_ctk/views/backup_view.py`:**
- Backup schedule configuration
- Backup history table (date, size, status)
- Backup retention policy settings
- Manual backup button
- Restore button (with file selection)
- Verify backup button
- Backup statistics (total size, count, oldest, newest)

## Proposed Solution

### Phase 1: Scheduler Integration (2 days)

**1.1 Add Scheduling Library**
```toml
# pyproject.toml
dependencies = [
    "schedule>=1.2.0",  # For backup scheduling
]
```

**1.2 Implement Backup Scheduler**
```python
# src/utils/backup_scheduler.py
import schedule
import time
from threading import Thread

class BackupScheduler:
    def __init__(self, backup_manager, config):
        self.backup_manager = backup_manager
        self.config = config
        self.running = False

    def start(self):
        """Start the backup scheduler."""
        if not self.config.get('automatic_daily', True):
            return

        backup_time = self.config.get('backup_time', '02:00')
        schedule.every().day.at(backup_time).do(self._run_backup)

        self.running = True
        Thread(target=self._run_scheduler, daemon=True).start()

    def _run_backup(self):
        """Run scheduled backup."""
        try:
            backup_path = self.backup_manager.create_backup(
                type='automatic',
                compress=True
            )
            self.backup_manager.verify_backup(backup_path)
            self.backup_manager.log_backup(backup_path, 'success')
        except Exception as e:
            self.backup_manager.log_backup(backup_path, 'failed', str(e))

    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)
```

### Phase 2: Backup Rotation (1-2 days)

```python
# src/utils/backup_rotation.py
from datetime import datetime, timedelta

class BackupRotation:
    def __init__(self, config):
        self.retention_days = config.get('retention_days', 30)
        self.backup_dir = config.get('backup_directory', './backups')

    def rotate_backups(self):
        """Rotate backups according to retention policy."""
        backups = self._list_backups()

        # Separate manual and automatic backups
        manual = [b for b in backups if b['type'] == 'manual']
        automatic = [b for b in backups if b['type'] == 'automatic']

        # Clean old automatic backups
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        to_delete = [b for b in automatic if b['date'] < cutoff_date]

        # Keep at least one backup per week for last 12 weeks
        # Keep at least one backup per month for last 12 months
        # (implement weekly/monthly retention logic)

        for backup in to_delete:
            self._delete_backup(backup['path'])

        return len(to_delete)
```

### Phase 3: Backup Verification (1 day)

```python
def verify_backup(backup_path: Path) -> bool:
    """Verify backup file integrity."""
    # Check file exists and has size
    if not backup_path.exists():
        return False
    if backup_path.stat().st_size < 1024:  # Too small
        return False

    # Try to decompress and open database
    try:
        temp_db = extract_backup(backup_path)
        conn = sqlite3.connect(temp_db)
        conn.execute("SELECT * FROM employees LIMIT 1")
        conn.close()
        return True
    except Exception:
        return False
```

### Phase 4: Backup Logging (1 day)

```python
# src/utils/backup_logger.py
import logging

class BackupLogger:
    def __init__(self, log_file):
        self.logger = logging.getLogger('backup')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    def log_backup_start(self, backup_type):
        self.logger.info(f"Backup started: {backup_type}")

    def log_backup_success(self, backup_path, duration, size):
        self.logger.info(f"Backup success: {backup_path.name}, "
                        f"duration: {duration}s, size: {size} bytes")

    def log_backup_failure(self, error):
        self.logger.error(f"Backup failed: {error}")

    def log_rotation(self, deleted_count):
        self.logger.info(f"Backup rotation: deleted {deleted_count} old backups")
```

### Phase 5: UI Enhancements (1-2 days)

**File: `src/ui_ctk/views/backup_view.py`**

Add:
1. Schedule configuration panel
2. Backup history table
3. Retention policy settings
4. Backup statistics dashboard
5. Real-time backup progress

## Dependencies

- **New dependency required:** `schedule>=1.2.0`
- Backup manager: 🟡 Partial (40% complete)
- Configuration system: ✅ Complete

## Related Issues

- ISSUE-011: No Backups Export (historical)
- ISSUE-012: No Logging Monitoring (historical)

## Acceptance Criteria

- [ ] Automatic daily backups work at scheduled time
- [ ] Backup rotation keeps last 30 days
- [ ] Backup rotation keeps weekly backups
- [ ] Backup rotation keeps monthly backups
- [ ] Manual backups never deleted automatically
- [ ] Backup verification works after creation
- [ ] Backup log records all operations
- [ ] Backup history shows in UI
- [ ] Schedule configuration works
- [ ] Retention policy configuration works
- [ ] Backup statistics accurate
- [ ] All tests pass

## Estimated Effort

**Total:** 5-6 days
- Scheduler integration: 2 days
- Backup rotation: 1-2 days
- Backup verification: 1 day
- Backup logging: 1 day
- UI enhancements: 1-2 days

## Notes

Automated backups are critical for production data protection. Data loss from disk failure, corruption, or user error would be catastrophic without automated backups.

## Backup Retention Strategy

**Recommended Default:**
- Daily backups: Keep last 30 days
- Weekly backups: Keep last 12 weeks (one per week)
- Monthly backups: Keep last 12 months (one per month)
- Manual backups: Keep forever (unless manually deleted)

**Storage Estimates:**
- Database size: ~1-5 MB (100 employees)
- Compressed backup: ~0.5-2 MB
- 30 daily backups: ~15-60 MB
- 12 weekly backups: ~6-24 MB
- 12 monthly backups: ~6-24 MB
- **Total:** ~27-108 MB (very manageable)

## References

- Python schedule library: https://schedule.readthedocs.io/
- Backup best practices: https://www.acquia.com/blog/drupal-backup-best-practices
- 3-2-1 backup strategy: https://www.backblaze.com/blog/the-3-2-1-backup-strategy/
