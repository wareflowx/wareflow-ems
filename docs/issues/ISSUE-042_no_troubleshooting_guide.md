# [HIGH] No Troubleshooting Guide

## Type
**Documentation / Support**

## Severity
**HIGH** - Long support resolution times, user frustration, recurring issues

## Affected Components
- **Troubleshooting** - Problem diagnosis and resolution
- **Support** - Ticket resolution
- **User Experience** - Recovering from errors

## Description

When errors occur, users have no guide for common issues, error messages, or recovery steps. Troubleshooting is trial-and-error, leading to long support resolution times, user frustration, and recurring problems.

## Current Troubleshooting Process

### What Users Do Today

**When error occurs**:
```
1. User sees error message
2. User doesn't understand error
3. User searches documentation (nothing relevant)
4. User searches GitHub Issues (fragmented info)
5. User tries random things
6. User gives up, submits support ticket
7. Support responds hours/days later
8. Issue resolved (eventually)
```

**Time to resolution**: Hours to days

## Real-World Impact

### Scenario 1: Database Lock Error

**Error message**:
```
Error: database is locked
Process cannot access the file because it is being used by another process
```

**User experience**:
```
User: "What does this mean?"
User: Searches documentation
User: Nothing about "database locked"
User: Searches GitHub Issues
User: Finds partial information
User: Tries various suggestions
User: None work
User: Submits support ticket
User: Waits 24 hours for response
Support: "Another instance is running"
User: Closes other instance
User: Problem solved
```

**With troubleshooting guide**:
```
User: Sees error
User: Opens Troubleshooting Guide
User: Searches "database locked"
User: Finds issue with solution:
  "Cause: Another instance running"
  "Solution: Close other instances or check locks"
User: Follows steps
User: Problem solved in 2 minutes
```

### Scenario 2: Configuration Validation Error

**Error message**:
```
Error: Invalid configuration
Critical days must be between 1 and 30
```

**User experience**:
```
User: "What did I do wrong?"
User: Opens config.yaml
User: Sees: critical_days: -1
User: "Why can't it be negative?"
User: "What should I set it to?"
User: Guesses: critical_days: 100
User: Error: Must be between 1 and 30
User: "But I want 100 days!"
User: Gives up, uses default
```

**With troubleshooting guide**:
```
User: Opens guide
User: Finds "Validation Errors" section
User: Sees explanation:
  "critical_days: Valid range 1-30"
  "Why: Critical alerts are for urgent issues"
  "If you want longer warnings, use info_days"
User: Understands the logic
User: Sets correct values
```

### Scenario 3: Application Won't Start

**Error message**:
```
Error: Application failed to initialize
```

**User experience**:
```
User: "Why won't it start?"
User: No useful error message
User: Searches logs
User: Logs are empty
User: Searches documentation
User: Nothing relevant
User: Submits ticket with minimal info:
  "Application doesn't work"
Support: "What's the error?"
User: "Just says failed to initialize"
Support: (remote session, 1 hour)
Support: "Config file missing"
User: "Oh, I deleted it"
Support: "Restore from backup or recreate"
User: "I don't have backup"
Support: "Recreate with wizard"
```

**With troubleshooting guide**:
```
User: Opens guide
User: Finds "Application Won't Start" section
User: Sees diagnostic steps:
  1. Check configuration exists
  2. Validate configuration
  3. Check database
  4. Check dependencies
  5. Run diagnostics
User: Follows steps
User: Discovers config file missing
User: Runs: wems init (recreate config)
User: Problem solved
```

## Common Issues (Undocumented)

### Bootstrapper Issues

1. **Directory already exists**
   - Error: "Target directory not empty"
   - Cause: Previous installation or files present
   - Solution: Use `--force` or choose different directory

2. **Invalid company name**
   - Error: "Invalid company name"
   - Cause: Special characters
   - Solution: Use alphanumeric, spaces, hyphens only

3. **Wizard abort**
   - Issue: User cancelled wizard
   - Problem: Partial state, must clean up
   - Solution: Delete incomplete directory

### Configuration Issues

4. **Invalid YAML syntax**
   - Error: "YAML parse error"
   - Cause: Indentation, colons, hyphens
   - Solution: Validate YAML, use editor

5. **Validation failed**
   - Error: "Value out of range"
   - Cause: Invalid config value
   - Solution: Check valid ranges in reference

6. **Missing required fields**
   - Error: "Required field missing"
   - Cause: Incomplete configuration
   - Solution: Add missing fields

### Database Issues

7. **Database locked**
   - Error: "database is locked"
   - Cause: Another instance running
   - Solution: Close other instances

8. **Database corrupted**
   - Error: "database malformed"
   - Cause: Improper shutdown, disk error
   - Solution: Restore from backup

9. **Migration failed**
   - Error: "Migration error"
   - Cause: Incompatible version, corruption
   - Solution: Restore backup, check logs

### Update Issues

10. **Download failed**
    - Error: "Download failed"
    - Cause: Network error, GitHub down
    - Solution: Check internet, retry

11. **Update verification failed**
    - Error: "Checksum mismatch"
    - Cause: Corrupted download
    - Solution: Redownload

12. **Migration rollback**
    - Error: "Migration failed"
    - Cause: Incompatible schema
    - Solution: `wems rollback`

### Performance Issues

13. **Slow startup**
    - Issue: Takes > 30 seconds to start
    - Cause: Large database, no indexing
    - Solution: Run `wems db vacuum`

14. **Slow queries**
    - Issue: Searches take > 5 seconds
    - Cause: Missing indexes
    - Solution: Add indexes

## Proposed Solution

### Solution 1: Comprehensive Troubleshooting Guide

**Structure**:
```markdown
# Troubleshooting Guide

## Quick Diagnosis

Start here: Run diagnostics
\`\`\`bash
wems doctor
\`\`\`

## Error Messages

### Bootstrapper Errors

#### "Directory already exists"

**Symptom**: Error when running \`wems init\`

**Cause**: Target directory contains files

**Solutions**:
1. Use \`--force\` to overwrite
2. Choose different directory with \`--output\`
3. Delete existing directory manually

**Prevention**: Check directory exists before init

#### "Invalid company name"

**Symptom**: Validation error during wizard

**Cause**: Special characters in company name

**Valid characters**: A-Z, a-z, 0-9, spaces, hyphens

**Examples**:
- ✓ Valid: "Acme Corp", "O'Reilly", "Company-Name"
- ✗ Invalid: "Company&Son", "Company@Inc", "Company/LLC"

### Configuration Errors

#### "Invalid YAML syntax"

**Symptom**: Config validation fails

**Common mistakes**:
- Wrong indentation (must use spaces, not tabs)
- Missing colons
- Missing hyphens for lists
- Unquoted special characters

**Quick fix**: Use online YAML validator
https://www.yamllint.com/

#### "Validation failed: value out of range"

**Symptom**: Specific value rejected

**Common ranges**:
- \`critical_days\`: 1-30
- \`warning_days\`: 1-90
- \`info_days\`: 1-365

**Solution**: Set value within valid range

### Database Errors

#### "database is locked"

**Symptom**: Cannot access database

**Cause**: Another instance running

**Solutions**:
1. Close other Wareflow EMS instances
2. Check for processes: \`wems lock status\`
3. Restart computer

**Prevention**: Use lock management

#### "database corrupted"

**Symptom**: Database appears malformed

**Causes**:
- Improper shutdown
- Disk error
- File system corruption

**Solutions**:
1. Restore from backup
2. Run \`wems db check\`
3. Run \`wems db repair\` (experimental)

**Prevention**: Regular backups

### Update Errors

#### "Download failed"

**Symptom**: Cannot download update

**Causes**:
- No internet connection
- GitHub down
- Firewall blocking

**Solutions**:
1. Check internet connection
2. Check GitHub status
3. Try again later
4. Download manually from GitHub

#### "Migration failed"

**Symptom**: Update migration failed

**Causes**:
- Database corrupted
- Incompatible version
- Missing migration scripts

**Solutions**:
1. Check logs: \`logs/wems.log\`
2. Run \`wems doctor\`
3. Restore from backup: \`wems rollback\`
4. Contact support with logs

## Getting Help

### Before Contacting Support

1. Run diagnostics: \`wems doctor\`
2. Check logs: \`logs/wems.log\`
3. Search this guide
4. Search GitHub Issues

### When Contacting Support

Include in your ticket:
1. Error message (exact text)
2. Steps to reproduce
3. Diagnostic output: \`wems doctor > output.txt\`
4. Log file: \`logs/wems.log\`
5. Screenshot (if applicable)

### Support Channels

- GitHub Issues: https://github.com/wareflowx/wareflow-ems/issues
- Email: support@wareflow.com (if available)
- Documentation: https://docs.wareflow.com

## Performance Issues

### Slow Startup

**Symptom**: Takes > 30 seconds to start

**Causes**:
- Large database
- Fragmented database
- Slow disk I/O

**Solutions**:
1. Run \`wems db vacuum\`
2. Check database size: \`wems db info\`
3. Check disk performance

### Slow Queries

**Symptom**: Searches take > 5 seconds

**Causes**:
- Missing indexes
- Large result sets
- Inefficient queries

**Solutions**:
1. Run \`wems db analyze\`
2. Add recommended indexes
3. Optimize queries
```

### Solution 2: Error Message Database

**Searchable database of errors**:

```markdown
## Error Messages Index

### A
- "Access denied"
- "Application failed to initialize"

### B
- "Backup failed"
- "Build error"

### C
- "Cannot connect to database"
- "Configuration validation failed"

# ... etc

Each error with:
- Error message
- Likely causes
- Solutions
- Prevention
- Related issues
```

### Solution 3: Interactive Diagnostics

**Integrated help**:

```python
# When error occurs
try:
    operation()
except Exception as e:
    print(f"Error: {e}")
    print("For help, run: wems doctor --error <error-code>")
    print("Or visit: https://docs.wareflow.com/troubleshooting#{error-code}")
```

### Solution 4: Video Tutorials

**Common troubleshooting scenarios**:

**Videos**:
1. "Diagnosing issues with wems doctor" (5 min)
2. "Fixing configuration errors" (10 min)
3. "Recovering from database corruption" (15 min)
4. "Rolling back failed updates" (10 min)

## Implementation Plan

### Phase 1: Core Guide (1 week)
1. Create troubleshooting guide structure
2. Document common errors
3. Add solutions
4. Add prevention tips

### Phase 2: Error Database (3 days)
1. Catalog all error messages
2. Index errors alphabetically
3. Add search function
4. Link errors to solutions

### Phase 3: Diagnostics Integration (3 days)
1. Add error codes to exceptions
2. Link errors to documentation
3. Improve error messages
4. Add "Get Help" buttons

### Phase 4: Video Tutorials (1 week)
1. Script videos
2. Record screencasts
3. Add voiceover
4. Upload to YouTube
5. Embed in documentation

## Files to Create

- `docs/user/troubleshooting.md`
- `docs/user/errors.md` - Error database
- `docs/user/quick-fixes.md`

## Files to Modify

- `src/utils/errors.py` - Add error codes
- `src/utils/logging.py` - Add error context
- All exception handling - Add helpful messages

## Benefits

### For Users
- **Self-service**: Fix issues themselves
- **Fast**: 2-minute resolution vs hours
- **Empowering**: Understand what went wrong
- **Confidence**: Know how to prevent issues

### For Support
- **Reduced burden**: Users solve own issues
- **Better tickets**: Users provide diagnostic info
- **Faster resolution**: Clear troubleshooting steps
- **Consistency**: Standardized solutions

### For Quality
- **Issue tracking**: See what problems users face
- **Improvement**: Identify areas needing better error messages
- **Prevention**: Add guides for common issues

## Success Metrics

- [ ] 80% of issues resolved with guide
- [ ] Average resolution time < 5 minutes
- [ ] Support tickets reduced by 70%
- [ ] User satisfaction > 4.5/5

## Related Issues

- #032: No Health Check or Diagnostic Tools (troubleshooting depends on diagnostics)
- #041: No User Documentation (troubleshooting is part of documentation)

## Priority

**HIGH** - Significantly improves support efficiency and user experience

## Estimated Effort

3 weeks (guide + error database + diagnostics + videos)

## Mitigation

While guide is being written:
1. Add FAQ to README
2. Document common errors in GitHub Issues
3. Create quick reference card
4. Add "Help" buttons in application
5. Provide email support for urgent issues
