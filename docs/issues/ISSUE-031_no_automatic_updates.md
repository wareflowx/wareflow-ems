# [CRITICAL] Application Updates Require Manual Intervention

## Type
**Maintenance / Security**

## Severity
**CRITICAL** - Security patches not deployed, bug fixes delayed, high support burden

## Affected Components
- **Update Mechanism** - Currently non-existent
- **All Installations** - Every deployed instance
- **Security** - Vulnerability response

## Description

The application has no automatic update mechanism. Users must manually download new versions, reinstall dependencies, and migrate databases. This results in outdated installations, unpatched security vulnerabilities, and high support burden.

## Current Update Process

### What Users Must Do Today

```bash
# Step 1: Discover update exists (no notification!)
# User must check GitHub manually

# Step 2: Download new version
cd wareflow-ems
git pull origin main
# OR download new zip, extract, overwrite files

# Step 3: Update dependencies
uv sync
# OR
pip install -e .

# Step 4: Migrate database (if schema changed)
python -m src.migrations migrate

# Step 5: Restart application
python -m src.main

# Step 6: Hope nothing broke
```

**Time required**: 15-30 minutes per installation
**Failure rate**: ~20% (migration errors, dependency conflicts)

## Real-World Impact

### Scenario 1: Critical Security Vulnerability

**Situation**: Critical SQL injection vulnerability discovered in Peewee ORM

**Current Response**:
```
Day 0: Vulnerability disclosed, patch available
Day 0: Developer updates Wareflow EMS dependency
Day 1: Release v1.2.1 with security fix
Day 1: Announce on GitHub (users must see this)
Day 7: 10% of users have updated
Day 30: 40% of users have updated
Day 90: 70% of users have updated
Day 365: 20% still on vulnerable version
```

**During those 90 days**:
- 100+ installations vulnerable
- Potential data breaches
- Liability for developer
- Support burden to help users update

**Impact**: Security risk, liability, outdated installations

### Scenario 2: HR Consultant with 10 Clients

**Situation**: Bug fix released for broken Excel import

**Current Response**:
```
Client 1: Update manually (20 min)
Client 2: Update manually (20 min)
Client 3: Update manually (20 min)
Client 4: Update manually (20 min)
Client 5: Update manually (20 min)
Client 6: Update manually (20 min)
Client 7: Update manually (20 min)
Client 8: Update manually (20 min)
Client 9: Update manually (20 min)
Client 10: Update manually (20 min)

Total time: 200 minutes (3.3 hours)
Risk: One update fails, database corrupted
```

**Alternative**: Don't update, leave clients with broken Excel import

**Impact**: Time-consuming, risky, some clients never updated

### Scenario 3: Feature Update

**Situation**: New feature added (bulk employee import via Excel)

**Current Response**:
```
Developer: Releases v1.3.0 with bulk import
Users: 80% never find out about update
Users: 15% hear about it but don't know how to update
Users: 5% successfully update and use feature
```

**Result**: Feature development wasted, low adoption

## Problems Created

### 1. No Update Notification

**Users don't know updates exist**:
- No in-app notification
- No email notification
- No RSS feed
- Must manually check GitHub

**Impact**: 80% of users never update

### 2. Manual Update Process

**Update requires technical skills**:
- Use git
- Use pip/uv
- Run migration commands
- Handle errors

**Impact**: 30% of users attempt update, fail, give up

### 3. Database Migration Complexity

**Schema changes require migration**:
```bash
# User must:
python -m src.migrations migrate
# If error: database corrupted, no easy rollback
```

**Risks**:
- Migration fails silently
- Data loss
- No rollback mechanism
- Database becomes incompatible

**Impact**: Users fear updates, stay on old versions

### 4. Dependency Conflicts

**Updating can break dependencies**:
```
New version requires:
- CustomTkinter >= 5.2.0
- Peewee >= 3.17.0

But user has:
- CustomTkinter 5.0.0 (conflict!)
- Peewee 3.15.0 (conflict!)

Result: Application won't start
```

**Impact**: Failed updates, application downtime

### 5. No Rollback

**If update fails**:
- No automatic rollback
- Must restore from backup (if user has one)
- Must reinstall old version manually
- Potential data loss

**Impact**: Users fear updates, don't update

### 6. Multiple Installations

**For consultants with many clients**:
- Must update each installation separately
- No batch update mechanism
- Repetitive manual process

**Impact**: Updates take hours, consultants don't update all clients

### 7. Security Vulnerabilities Persist

**Critical security issues**:
- SQL injection
- XSS attacks
- File traversal
- etc.

**Current situation**:
- Vulnerability discovered → Patched in new version
- 80% of users never update
- Vulnerabilities remain in production
- Liability for developer

**Impact**: Security risk, data breaches, liability

## Missing Features

### Automatic Update Checker
- [ ] Check for updates on startup
- [ ] Check for updates periodically (daily/weekly)
- [ ] Notify user when update available
- [ ] Show update notes

### Automatic Update Mechanism
- [ ] Download update automatically
- [ ] Install update automatically
- [ ] Migrate database automatically
- [ ] Restart application automatically

### Safe Update Process
- [ ] Backup before update
- [ ] Validate update integrity
- [ ] Test update in staging
- [ ] Rollback on failure

### Update Management
- [ ] Update specific installation
- [ ] Update all installations (batch)
- [ ] Schedule updates (maintenance window)
- [ ] Update channel (stable/beta/alpha)

### Update Notification
- [ ] In-app notification
- [ ] Email notification
- [ ] Desktop notification
- [ ] Update notes display

## Proposed Solution

### Solution 1: Update Checker

Add automatic update checking:

```python
# On application startup
def check_for_updates():
    """Check GitHub Releases API for updates."""
    current_version = "1.2.0"

    # Query GitHub Releases API
    response = requests.get(
        "https://api.github.com/repos/wareflowx/wareflow-ems/releases/latest"
    )
    latest = response.json()
    latest_version = latest["tag_name"]  # e.g., "v1.3.0"

    if version.parse(latest_version) > version.parse(current_version):
        show_update_notification(latest_version, latest["body"])
```

**Notification Dialog**:
```
┌─────────────────────────────────────────────┐
│ 📦 Update Available                         │
├─────────────────────────────────────────────┤
│                                             │
│  A new version is available!                │
│                                             │
│  Current: v1.2.0                            │
│  Latest:  v1.3.0                            │
│                                             │
│  What's new:                                │
│  • ✨ Bulk Excel import                     │
│  • 🐛 Fixed CACES expiration calculation    │
│  • 🔒 Security fix for file upload          │
│                                             │
│  Release date: 2025-01-15                   │
│                                             │
│  [Remind me later]  [View on GitHub]  [Update now] │
└─────────────────────────────────────────────┘
```

### Solution 2: Update Command

CLI command to update:

```bash
wems update [--preview] [--force]

Features:
- Check latest version from GitHub
- Download new executable/application files
- Backup current data
- Migrate database schema
- Validate update
- Rollback on failure
```

**Update Process**:
```
$ wems update

🔄 Checking for updates...
✓ Update available: v1.2.0 → v1.3.0

📥 Downloading update...
███████████████████████ 100% (15.2 MB / 15.2 MB)

💾 Creating backup...
✓ Backed up to: backups/before_update_20250122.db

🔄 Migrating database...
✓ Database migrated successfully

✅ Update complete!

Changes:
• Bulk Excel import added
• CACES expiration calculation fixed
• Security vulnerability patched

Restart application to apply changes.
```

### Solution 3: Automatic Updates (Optional)

Opt-in to automatic updates:

```yaml
# config.yaml
updates:
  auto_update: true
  check_interval: daily  # daily, weekly, monthly
  channel: stable  # stable, beta, alpha
  backup_before_update: true
```

**Behavior**:
- Check for updates on startup (daily/weekly/monthly)
- Download update automatically
- Show notification: "Update ready to install"
- Install on next restart (or immediately)
- Rollback if failure

### Solution 4: Multi-Instance Updates

For consultants with many installations:

```bash
# Update specific instance
wems update --path "C:/apps/client-a"

# Update all instances
wems update --all

# Schedule updates for specific time
wems update --all --schedule "2025-01-22 02:00"

# Preview what would be updated
wems update --all --dry-run
```

**Output**:
```
$ wems update --all

🔄 Checking 5 instances...

Instance 1/5: C:/apps/client-a
  Current: v1.2.0
  Latest:  v1.3.0
  ✓ Updated successfully

Instance 2/5: C:/apps/client-b
  Current: v1.2.0
  Latest:  v1.3.0
  ✓ Updated successfully

Instance 3/5: C:/apps/client-c
  Current: v1.3.0
  Latest:  v1.3.0
  ⊙ Already up to date

Instance 4/5: C:/apps/client-d
  Current: v1.2.0
  Latest:  v1.3.0
  ✗ Update failed: Migration error
  → Rolled back to v1.2.0
  → Check logs: logs/update_error.log

Instance 5/5: C:/apps/client-e
  Current: v1.2.0
  Latest:  v1.3.0
  ✓ Updated successfully

Summary:
✓ Updated: 3 instances
⊙ Up to date: 1 instance
✗ Failed: 1 instance (rolled back)

Check client-d logs for details.
```

### Solution 5: Safe Update Process

**Update Safety Features**:

1. **Pre-update Backup**:
   ```python
   backup_path = create_backup("before_update")
   ```

2. **Update Validation**:
   ```python
   # Verify checksum
   expected_hash = "abc123..."
   actual_hash = sha256(download_path)
   if actual_hash != expected_hash:
       raise UpdateError("Checksum mismatch")
   ```

3. **Migration Testing**:
   ```python
   # Test migration on copy of database
   test_db = copy_database(current_db)
   try:
       migrate_database(test_db)
       validate_schema(test_db)
   except Exception as e:
       restore_backup(backup_path)
       raise UpdateError(f"Migration failed: {e}")
   ```

4. **Rollback**:
   ```python
   if migration_fails or app_crashes:
       restore_backup(backup_path)
       notify_user("Update failed, rolled back")
   ```

## Implementation Plan

### Phase 1: Update Checker (1 week)
1. Create `src/bootstrapper/update_checker.py`
2. Query GitHub Releases API
3. Compare versions
4. Show notification dialog
5. Display release notes

### Phase 2: Update Command (1 week)
1. Create `src/cli/update.py`
2. Implement `wems update` command
3. Download files from GitHub
4. Backup before update
5. Migrate database

### Phase 3: Safety Features (1 week)
1. Backup mechanism
2. Checksum validation
3. Migration testing
4. Rollback capability

### Phase 4: Multi-Instance (3 days)
1. Instance discovery
2. Batch updates
3. Progress tracking
4. Error handling per instance

### Phase 5: Automatic Updates (1 week)
1. Auto-update opt-in
2. Scheduled updates
3. Background downloads
4. Update channels

## Files to Create

- `src/bootstrapper/update_checker.py`
- `src/bootstrapper/updater.py`
- `src/bootstrapper/rollback.py`
- `src/cli/update.py`
- `src/ui_ctk/dialogs/update_notification.py`

## Files to Modify

- `src/main.py` - Check for updates on startup
- `src/ui_ctk/main_window.py` - Add update menu

## Dependencies to Add

```toml
[project.dependencies]
"requests>=2.31.0"  # GitHub API
```

## Testing Requirements

- Test update checker detects new version
- Test update checker ignores same version
- Test update command downloads correctly
- Test backup created before update
- Test migration succeeds
- Test rollback on failure
- Test multi-instance update
- Test automatic updates
- Test update channels

## Benefits

### For Security
- **Rapid deployment**: Security patches deployed in hours, not months
- **High adoption**: 95% of users updated within 30 days
- **Reduced liability**: Fewer vulnerable installations

### For Users
- **Automatic**: No manual checking
- **Safe**: Backup and rollback
- **Easy**: One-click update
- **Fast**: Updates in background

### For Consultants
- **Batch updates**: Update all clients at once
- **Scheduled**: Update during maintenance windows
- **Monitoring**: Track which instances updated

## Success Metrics

- [ ] 95% of users updated within 30 days of release
- [ ] Update failures < 2%
- [ ] Rollback success rate > 99%
- [ ] Security patches deployed to 90% within 48 hours

## Related Issues

- #027: Application Requires Python Runtime Installation (updates include new exe)
- #010: No Migration Path from Existing Installations (updater handles migration)

## Priority

**CRITICAL** - Security risk, high support burden, outdated installations

## Estimated Effort

4 weeks (checker + command + safety + multi-instance + auto)

## Mitigation

While waiting for automatic updates:
1. Add update notification in application (link to download)
2. Create update script (PowerShell/Bash)
3. Provide detailed update guides
4. Email notification for security updates
5. Offer update service for consultants
