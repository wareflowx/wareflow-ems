# [MEDIUM] No Health Check or Diagnostic Tools

## Type
**Operations / Troubleshooting**

## Severity
**MEDIUM** - Significantly increases support burden and troubleshooting time

## Affected Components
- **Troubleshooting** - Diagnosing issues
- **Support** - Identifying root causes
- **Operations** - System health monitoring

## Description

When issues occur, there is no way to diagnose database corruption, configuration errors, file permission problems, or performance issues. Troubleshooting is trial-and-error, leading to long support resolution times and user frustration.

## Current Troubleshooting Process

### What Happens When User Reports Issue

#### User Experience:
```
1. User encounters error
2. User submits support ticket: "Application doesn't work"
3. Support asks: "What's the error?"
4. User: "I don't know, just doesn't work"
5. Support asks: "Check logs"
6. User: "Where are logs?"
7. Support: "In logs/ directory"
8. User: "Empty, no logs"
9. Support: "Check database"
10. User: "How?"
11. Support: (remote session, 30 minutes of investigation)
12. Support: "Ah, database file is corrupted"
13. Support: "Restore from backup"
14. User: "I don't have backup"
15. Support: "You're out of luck, sorry"
```

**Time to resolution**: 2-4 hours
**User satisfaction**: Very low

#### Support Experience:
```
Ticket #1234: "Application crashes on startup"

Support (trial and error):
- Check logs: Empty
- Check config: Looks fine
- Check database: How to validate?
- Check permissions: Can't verify remotely
- Check dependencies: Which ones?
- Check Python version: User doesn't know
- Check disk space: User doesn't know where to check

After 2 hours: "Can you run this diagnostic command?"
User: "I don't know how to open terminal"

Resolution: Remote desktop session (another hour)
Root cause: Database file was on network drive, lost connection
Fix: Move database to local drive

Time spent: 3 hours
Should have been: 5 minutes with diagnostic tool
```

## Real-World Impact

### Scenario 1: Slow Performance

**User Report**: "Application is very slow"

**Current Investigation**:
```
Support: "How slow?"
User: "Like, really slow"
Support: "How many employees?"
User: "I don't know, maybe 100?"
Support: "Check disk space"
User: "How?"
Support: "Open File Explorer, right-click C:, Properties"
User: "45 GB free"
Support: "Check if database is locked"
User: "How do I check?"
Support: (remote session)

After 1 hour: Found database was 2 GB, never vacuumed
Fix: Should have run VACUUM, but no tool to detect this
```

**With diagnostic tool**:
```bash
$ wems doctor

🔍 Database Health
─────────────────────────────
Size: 2.1 GB (WARNING: Large database)
Pages: 125,000
Fragmentation: 45% (WARNING: Should be < 10%)
Last vacuum: Never (WARNING: Should be monthly)

💡 Recommendation: Run VACUUM to optimize database
   Command: wems db vacuum
```

**Time to diagnosis**: 5 seconds
**Time to resolution**: 2 minutes

### Scenario 2: Application Won't Start

**User Report**: "Application shows error then closes"

**Current Investigation**:
```
User: "I click icon, error flashes, then nothing"
Support: "What's the error?"
User: "Too fast to read"
Support: "Check logs"
User: "logs/ is empty"
Support: "Check config"
User: "What config?"
Support: "data/config.yaml"
User: "Doesn't exist"
Support: "Did you install correctly?"
User: "I just extracted zip"
Support: "You need to run init"
User: "How?"
Support: (long explanation, user confused)

After 45 minutes: User hadn't initialized database
Fix: Run database init
```

**With diagnostic tool**:
```bash
$ wems doctor

🔍 Application Health
─────────────────────────────
✓ Python version: 3.14.1 (OK)
✓ Dependencies: All installed (OK)
✗ Database: Not initialized (ERROR)
  → Run: wems init

🔧 Quick Fix
─────────────────────────────
Would you like to initialize the database now? [Y/n]: Y
✓ Database initialized

✅ All checks passed! Try starting the application again.
```

**Time to diagnosis**: 5 seconds
**Time to resolution**: 30 seconds

### Scenario 3: Intermittent Crashes

**User Report**: "Application crashes randomly"

**Current Investigation**:
```
Support: "When does it crash?"
User: "Random, maybe once a day"
Support: "Check logs"
User: "Nothing useful in logs"
Support: "Check disk space"
User: "Plenty"
Support: "Check if file is locked"
User: "How?"
Support: (remote session, 1 hour)

Found: Database on network drive, occasional connection drops
Network latency causing locks to timeout
```

**With diagnostic tool**:
```bash
$ wems doctor

🔍 Database Health
─────────────────────────────
Path: \\server\share\data\employee_manager.db
Location: Network drive (WARNING: Not recommended)

⚠️  Potential Issues:
  • Network latency can cause locks to timeout
  • Intermittent connection drops can corrupt database
  • Concurrent access may be slow

💡 Recommendation: Move database to local drive
   Current: \\server\share\data\employee_manager.db
   Suggested: C:\WareflowEMS\data\employee_manager.db

Performance: Last query took 2.5s (WARNING: Should be < 100ms)
Lock timeouts detected: 15 times
Network latency: 45ms average
```

**Time to diagnosis**: 5 seconds
**Root cause identified immediately**

## Problems Created

### 1. No System Overview

**Support can't see**:
- Database health (size, fragmentation, corruption)
- Configuration validity
- File permissions
- Disk space
- Application version
- Dependency versions

**Impact**: Trial-and-error troubleshooting

### 2. No Validation

**Users don't know if**:
- Database is corrupted
- Configuration is valid
- Files have correct permissions
- Dependencies are satisfied

**Impact**: Issues persist until catastrophic failure

### 3. No Performance Monitoring

**Can't identify**:
- Slow queries
- Large database
- Missing indexes
- Lock contention
- Disk I/O issues

**Impact**: Performance degrades over time, unnoticed

### 4. No Proactive Alerts

**No warnings for**:
- Database getting large
- Backup getting old
- Disk space low
- Database needs vacuum
- Configuration errors

**Impact**: Issues discovered too late

### 5. No Root Cause Analysis

**When errors occur**:
- Don't know why
- Can't reproduce
- Can't prevent recurrence
- No historical data

**Impact**: Same issues repeat

## Missing Features

### Health Check Command
- [ ] Database integrity check
- [ ] Configuration validation
- [ ] File permission check
- [ ] Disk space check
- [ ] Dependency version check

### Performance Analysis
- [ ] Query performance
- [ ] Database size analysis
- [ ] Fragmentation check
- [ ] Index usage
- [ ] Lock contention

### Diagnostics
- [ ] Error log analysis
- [ ] Crash detection
- [ ] Historical health tracking
- [ ] Performance trends

### Recommendations
- [ ] Automatic issue detection
- [ ] Suggested fixes
- [ ] Quick fix commands
- [ ] Best practices validation

## Proposed Solution

### Solution 1: Doctor Command

Create comprehensive diagnostic command:

```bash
wems doctor [--full] [--json] [--fix]
```

**Output**:
```bash
$ wems doctor

🏥 Wareflow EMS Health Check
════════════════════════════════

[1/6] Application Status
─────────────────────────────
✓ Version: 1.2.0
✓ Latest: 1.2.0 (up to date)
✓ Python: 3.14.1
✓ Platform: Windows 11

[2/6] Dependencies
─────────────────────────────
✓ CustomTkinter: 5.2.0
✓ Peewee: 3.17.0
✓ OpenPyXL: 3.1.2
✓ All dependencies satisfied

[3/6] Database Health
─────────────────────────────
✓ Database exists: data/employee_manager.db
✓ Size: 45.2 MB
✓ Integrity: OK
✓ Schema: v1.2.0 (up to date)
✓ Last backup: 2 days ago
✗ Fragmentation: 35% (WARNING: Should be < 10%)
  💡 Run: wems db vacuum

[4/6] Configuration
─────────────────────────────
✓ Config file exists: config.yaml
✓ Valid YAML syntax
✓ All required fields present
✓ Valid values
✗ Database path: relative path (WARNING)
  💡 Use absolute path for reliability

[5/6] File Permissions
─────────────────────────────
✓ Database: Read/Write
✓ Documents/: Read/Write
✓ Backups/: Read/Write
✓ Logs/: Read/Write

[6/6] Disk Space
─────────────────────────────
✓ C: drive: 45.2 GB free (OK)
✓ Database location: OK

════════════════════════════════
Summary: 5 OK, 2 warnings, 0 errors

Recommendations:
1. Run VACUUM to reduce database fragmentation
2. Use absolute path for database location

Quick fix: wems doctor --fix
```

### Solution 2: Individual Checks

Allow checking specific components:

```bash
# Check database only
wems doctor --check database

# Check configuration only
wems doctor --check config

# Check performance only
wems doctor --check performance

# Full detailed check
wems doctor --full

# Output as JSON (for automation)
wems doctor --json
```

### Solution 3: Auto-Fix

Automatically fix common issues:

```bash
$ wems doctor --fix

🔧 Auto-Fix Mode
─────────────────────────────

Issue: Database fragmentation 35%
Fix: Running VACUUM...
✓ Database optimized (45.2 MB → 38.1 MB)

Issue: Relative database path
Fix: Converting to absolute path...
✓ Updated config.yaml

Issue: Old log files
Fix: Cleaning logs older than 30 days...
✓ Deleted 12 log files

✅ All issues fixed!
```

### Solution 4: Performance Analysis

Detailed performance diagnostics:

```bash
$ wems doctor --performance

📊 Performance Analysis
─────────────────────────────

Database Statistics:
  Size: 45.2 MB
  Tables: 5
  Indexes: 12
  Fragmentation: 35% ⚠️

Query Performance:
  Last query: 125ms ✓
  Average query: 45ms ✓
  Slow queries (> 1s): 0 ✓

Lock Statistics:
  Lock waits: 0
  Lock timeouts: 0
  Deadlocks: 0

Index Usage:
  employees.external_id: 95% used ✓
  employees.status: 82% used ✓
  caces.employee_id: 78% used ✓

Recommendations:
1. Run VACUUM to reduce fragmentation
2. All indexes are being used effectively
```

### Solution 5: Historical Tracking

Track health over time:

```bash
$ wems doctor --history

📈 Health History (Last 30 days)
─────────────────────────────

Database Size:
  Jan 1: 38.2 MB
  Jan 15: 42.1 MB
  Jan 22: 45.2 MB
  Trend: +1.2 MB/week

Fragmentation:
  Jan 1: 12%
  Jan 15: 28% ⚠️
  Jan 22: 35% ⚠️
  Trend: Increasing

Backups:
  Last backup: 2 days ago ✓
  Oldest backup: 30 days ago
  Backup retention: OK

Errors:
  Last 7 days: 0 ✓
  Last 30 days: 2 (fixed)

Recommendation: Schedule weekly VACUUM
```

## Implementation Plan

### Phase 1: Core Doctor Command (1 week)
1. Create `src/cli/doctor.py`
2. Implement health checks
3. Add database validation
4. Add config validation
5. Add file permission check

### Phase 2: Additional Checks (1 week)
1. Disk space check
2. Dependency validation
3. Version checking
4. Performance analysis
5. Log analysis

### Phase 3: Auto-Fix (1 week)
1. Implement auto-fix framework
2. Add VACUUM command
3. Add config fixer
4. Add permission fixer
5. Add cleanup commands

### Phase 4: Advanced Features (3 days)
1. Historical tracking
2. Performance monitoring
3. Trend analysis
4. Alerts and notifications

## Files to Create

- `src/cli/doctor.py`
- `src/bootstrapper/diagnostics.py`
- `src/bootstrapper/health_checks.py`
- `src/utils/db_validator.py`
- `src/utils/config_validator.py`

## Files to Modify

- `src/cli/__init__.py` - Add doctor command

## Testing Requirements

- Test all health checks pass/fail correctly
- Test doctor detects common issues
- Test auto-fix resolves issues
- Test JSON output format
- Test performance analysis accuracy
- Test historical tracking

## Benefits

### For Users
- **Self-service**: Can diagnose issues themselves
- **Clarity**: Understand what's wrong
- **Quick**: 5-second diagnosis vs hours
- **Proactive**: Catch issues before they're critical

### For Support
- **Efficiency**: Quick diagnosis
- **Remote**: User can run and share output
- **Consistency**: Standardized troubleshooting
- **Reduced burden**: 80% fewer support tickets

### For Operations
- **Monitoring**: Track health over time
- **Trends**: Identify degradation
- **Prevention**: Fix issues before failure
- **Performance**: Optimize based on data

## Success Metrics

- [ ] Average time to diagnosis reduced from 2 hours to 2 minutes
- [ ] 80% of issues resolved without support intervention
- [ ] User satisfaction score > 4.5/5
- [ ] Support ticket volume reduced by 70%

## Related Issues

- #031: Application Updates Require Manual Intervention (doctor checks updates)
- #010: No Migration Path from Existing Installations (doctor validates migrations)

## Priority

**MEDIUM** - Significantly improves support efficiency but doesn't block functionality

## Estimated Effort

3 weeks (core + checks + auto-fix + advanced)

## Mitigation

While waiting for doctor command:
1. Provide troubleshooting guide in documentation
2. Create manual diagnostic script
3. Add logging to help identify issues
4. Create FAQ for common issues
5. Offer remote desktop support
