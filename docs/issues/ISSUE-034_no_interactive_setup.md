# [MEDIUM] No Interactive Setup for New Installations

## Type
**User Experience / Onboarding**

## Severity
**MEDIUM** - High barrier to first-time users, increases abandonment

## Affected Components
- **Initial Setup** - First-time installation
- **Onboarding** - New user experience
- **Configuration** - Initial configuration

## Description

First-time setup requires reading documentation, manually creating directories, and editing configuration files. No guided setup wizard exists, creating a high barrier to entry and poor first impression.

## Current First-Time Experience

### What New Users Must Do

#### Step 1: Download and Extract
```
User: Downloads wareflow-ems.zip
User: Extracts to folder
User: Sees files, doesn't know what to do next
```

#### Step 2: Read Documentation
```
User: Opens README.md
User: Sees 20+ sections
User: Skips to "Installation"
User: Sees commands:
  uv sync
  uv run python -m src.main
User: "What's uv? What's python?"
```

#### Step 3: Install Dependencies
```
User: Tries to figure out installation
User: Installs Python
User: Installs uv
User: Runs commands
User: (30 minutes later)
```

#### Step 4: Create Directories
```
User: Reads documentation: "Create data/ directory"
User: Creates data/
User: "What else do I need?"
User: Creates documents/
User: Creates backups/
User: "Is this right?"
```

#### Step 5: Configure
```
User: Opens config.py or .env
User: Sees settings:
  DATABASE_PATH = "employee_manager.db"
  ALERT_CRITICAL_DAYS = 7
User: "What should I set these to?"
User: "What's a reasonable value?"
User: Guesses values
```

#### Step 6: Initialize Database
```
User: Runs command
User: "Is it working? Did I do it right?"
User: Tries to start application
User: (hopefully works)
```

**Total time**: 1-2 hours
**Abandonment rate**: ~40%

## Real-World Impact

### Scenario 1: Warehouse Manager (Non-Technical)

**User Profile**:
- Manages 50 employees
- Wants to track CACES certifications
- Comfortable with Excel, not command line

**Experience**:
```
1. Downloads Wareflow EMS
2. Extracts files
3. Opens README.md
4. Sees technical instructions
5. "uv sync? What's that?"
6. Tries to figure it out
7. Gives up after 20 minutes
8. Returns to Excel spreadsheets
```

**Result**: Lost customer, negative word-of-mouth

### Scenario 2: HR Consultant Evaluating Software

**User Profile**:
- Technical consultant
- Evaluating software for clients
- Wants quick demo

**Experience**:
```
1. Downloads software
2. Wants to test quickly
3. Sees complex installation
4. "This will take too long"
5. Skips to competitor software
6. Competitor has 5-minute setup
7. Chooses competitor
```

**Result**: Lost business opportunity

### Scenario 3: Student Learning About HR Software

**User Profile**:
- Learning about warehouse management
- Wants to try software
- Limited time

**Experience**:
```
1. Finds Wareflow EMS online
2. "Looks interesting!"
3. Downloads software
4. Sees complex setup
5. "I don't have time for this"
6. Abandons
7. Never tries the software
```

**Result**: Lost potential user, negative review

## Problems Created

### 1. High Barrier to Entry

**Users must**:
- Understand command line
- Install Python
- Install package manager
- Create directory structure
- Edit configuration files
- Initialize database

**Impact**: 40% abandonment rate

### 2. No Guidance

**Users are left guessing**:
- What directories to create?
- What configuration values to set?
- What's a "reasonable" alert threshold?
- What roles should I define?

**Impact**: Analysis paralysis, abandoned installations

### 3. Poor First Impression

**First experience**:
- Complex, technical
- Time-consuming
- Error-prone
- Frustrating

**Impact**: "This is too complicated", bad reviews

### 4. No Validation

**Users don't know if**:
- Installation is correct
- Configuration is valid
- Database initialized properly
- Ready to use

**Impact**: Uncertainty, fear of breaking something

### 5. Time-Consuming

**Setup time**:
- Documentation: 15 minutes reading
- Installation: 30 minutes installing dependencies
- Configuration: 15 minutes editing files
- Testing: 15 minutes verifying

**Total**: 1-1.5 hours

**Impact**: Users give up or choose competitors

## Missing Features

### Interactive Setup Wizard
- [ ] Guided step-by-step setup
- [ ] Questions with helpful defaults
- [ ] Validation during setup
- [ ] Progress indication
- [ ] Preview before finalizing

### First-Run Detection
- [ ] Detect first launch
- [ ] Launch wizard automatically
- [ ] Skip if config exists
- [ ] Re-run on demand

### Smart Defaults
- [ ] Sensible default values
- [ ] Industry presets
- [ ] Company-specific suggestions
- [ ] Best practices built-in

### Quick Start
- [ ] "Express setup" option
- [ ] All defaults, just confirm
- [ ] 5-minute setup time

## Proposed Solution

### Interactive Setup Wizard

**First launch detection**:
```python
# On first run
if not config_file_exists():
    launch_setup_wizard()
```

**Wizard interface** (CLI):
```bash
$ wems start

🎉 Welcome to Wareflow EMS!
═══════════════════════════

This wizard will help you get started.

It looks like this is your first time running Wareflow EMS.
Let's set up your application.

[Step 1/6] Basic Information
────────────────────────────

Company name (optional): [My Warehouse]
  💡 Leave empty to skip

Your name (optional): [John Doe]
  💡 For identification in records

[Step 2/6] Organization
────────────────────────────

Workspaces (comma-separated, press Enter for defaults):
  [Quai, Zone A, Zone B, Bureau]

Roles (comma-separated, press Enter for defaults):
  [Cariste, Magasinier, Préparateur]

[Step 3/6] Alerts
────────────────────────────

Alert when CACES/visits expire within (days):
  Critical: [7]   Warning: [30]   Info: [90]
  💡 These are recommended defaults

[Step 4/6] Database
────────────────────────────

Database location (press Enter for default):
  [data/employee_manager.db]

Backup retention (days, press Enter for default):
  [30]

[Step 5/6] Interface
────────────────────────────

Window title (press Enter for default):
  [Wareflow EMS]

Theme: [System] (1: Light, 2: Dark, 3: System) [3]

[Step 6/6] Review & Create
────────────────────────────

Company: My Warehouse
Workspaces: Quai, Zone A, Zone B, Bureau (4)
Roles: Cariste, Magasinier, Préparateur (3)
Alerts: Critical=7d, Warning=30d, Info=90d
Database: data/employee_manager.db

Everything looks correct? [Y/n]: Y

✅ Configuration saved
✅ Directories created
✅ Database initialized
✅ Ready to use!

Starting application...
```

### Express Setup Mode

**Quick start** (all defaults):
```bash
$ wems start --express

🚀 Express Setup
════════════════

Using default configuration:
• Workspaces: Quai, Zone A, Zone B, Bureau
• Roles: Cariste, Magasinier, Préparateur
• Alerts: 7/30/90 days
• Database: data/employee_manager.db

Creating your application...
✅ Configuration saved
✅ Directories created
✅ Database initialized

✅ Ready! Starting application...
```

**Time**: 2 minutes

### Re-run Wizard

**Change configuration later**:
```bash
$ wems configure

⚙️  Configuration Wizard
════────────────────────

Current settings:
• Company: My Warehouse
• Workspaces: Quai, Zone A, Zone B, Bureau

Update configuration? [Y/n]:
```

### GUI Wizard (Future)

**For desktop application**:
```
┌─────────────────────────────────────────────┐
│ Welcome to Wareflow EMS!            [Skip] │
├─────────────────────────────────────────────┤
│                                              │
│  Let's get you set up in a few minutes.     │
│                                              │
│  [Step 1 of 6]                               │
│  ●○○○○○                                      │
│                                              │
│  Company Information                         │
│  ─────────────────────────────────────       │
│                                              │
│  Company name:                               │
│  ┌──────────────────────────────────┐        │
│  │ My Warehouse                      │        │
│  └──────────────────────────────────┘        │
│                                              │
│  Your name (optional):                       │
│  ┌──────────────────────────────────┐        │
│  │ John Doe                           │        │
│  └──────────────────────────────────┘        │
│                                              │
│             [← Back]  [Next →]               │
└─────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Detection Framework (2 days)
1. Detect first run
2. Check if config exists
3. Launch wizard automatically
4. Add `--skip-wizard` flag

### Phase 2: CLI Wizard (1 week)
1. Create `src/bootstrapper/setup_wizard.py`
2. Implement step-by-step questions
3. Add validation
4. Add progress indication
5. Add review step

### Phase 3: Express Mode (2 days)
1. Add `--express` flag
2. Use all defaults
3. Quick confirmation
4. Fast path for technical users

### Phase 4: Configuration (3 days)
1. Save configuration
2. Create directories
3. Initialize database
4. Validate setup
5. Launch application

## Files to Create

- `src/bootstrapper/setup_wizard.py`
- `src/bootstrapper/first_run.py`
- `src/cli/configure.py`

## Files to Modify

- `src/main.py` - Detect first run, launch wizard
- `src/utils/config.py` - Support wizard output

## Testing Requirements

- Test wizard detects first run correctly
- Test wizard skips if config exists
- Test express mode works
- Test validation catches invalid inputs
- Test user can go back and change answers
- Test configuration is saved correctly
- Test directories are created
- Test database is initialized
- Test application launches after setup

## Benefits

### For New Users
- **Easy**: No manual configuration
- **Fast**: 5-10 minutes vs 1-2 hours
- **Guided**: Helpful hints and defaults
- **Confident**: Validation ensures correctness

### For Adoption
- **Lower barrier**: More users complete setup
- **Better impression**: Smooth onboarding
- **Reduced abandonment**: < 5% abandonment vs 40%

### For Support
- **Fewer issues**: Validated configuration
- **Consistent**: All setups use same structure
- **Self-service**: Users can re-run wizard

## Success Metrics

- [ ] Setup time reduced from 1-2 hours to 5-10 minutes
- [ ] Abandonment rate reduced from 40% to < 5%
- [ ] User satisfaction score > 4.5/5 for setup
- [ ] 90% of users use express mode or complete wizard

## Related Issues

- #028: Each Installation Requires Manual Configuration (wizard solves this)
- #027: Application Requires Python Runtime Installation (wizard is part of bootstrapper)

## Priority

**MEDIUM** - Significantly improves onboarding but setup is possible without it

## Estimated Effort

2 weeks (wizard + express + configuration + testing)

## Mitigation

While waiting for wizard:
1. Create detailed setup guide with screenshots
2. Provide setup video tutorials
3. Create one-click setup script
4. Add "Quick Start" section to README
5. Offer remote setup assistance
