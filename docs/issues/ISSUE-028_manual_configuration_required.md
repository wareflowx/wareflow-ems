# [HIGH] Each Installation Requires Manual Configuration

## Type
**Configuration / User Experience**

## Severity
**HIGH** - Significantly increases deployment time, error-prone, inconsistent setups

## Affected Components
- **Initial Setup** - First-time configuration
- **Configuration Files** - Company-specific settings
- **Directory Structure** - File system organization
- **Database** - Schema initialization

## Description

Every new installation of Wareflow EMS requires manual configuration with no standardized setup process. Users must manually create directories, edit configuration files, initialize databases, and customize settings. This creates a high barrier to entry and leads to inconsistent, error-prone deployments.

## Current Manual Configuration Process

### What Users Must Do Manually

#### Step 1: Create Directory Structure

```bash
# User must figure out correct structure and create manually
mkdir wareflow-ems
cd wareflow-ems
mkdir data
mkdir documents
mkdir documents/caces
mkdir documents/medical
mkdir documents/training
mkdir backups
mkdir logs
mkdir templates
```

**Common errors**:
- Wrong directory names
- Wrong nesting level
- Missing directories
- Wrong permissions

#### Step 2: Edit Configuration Files

```python
# User must create and edit config.py or .env
DATABASE_PATH = "data/employee_manager.db"
BACKUP_RETENTION = 30
ALERT_CRITICAL_DAYS = 7
ALERT_WARNING_DAYS = 30

# Or edit .env file
DATABASE_PATH=data/employee_manager.db
BACKUP_RETENTION=30
ALERT_CRITICAL_DAYS=7
ALERT_WARNING_DAYS=30
```

**Common errors**:
- Syntax errors in Python files
- Wrong file paths
- Invalid values
- Incorrect format

#### Step 3: Configure Organization

```python
# User must manually edit lists
WORKSPACES = ["Quai", "Zone A", "Zone B"]  # How to know these?
ROLES = ["Cariste", "Magasinier", "Préparateur"]  # What are valid roles?
CONTRACT_TYPES = ["CDI", "CDD", "Intérim"]  # What about Alternance?
```

**Common errors**:
- Typos in values
- Inconsistent terminology
- Missing common values
- Non-standard contract types

#### Step 4: Initialize Database

```bash
# User must run database initialization
python -c "from database.connection import init_database; init_database()"

# Or use CLI (if they know about it)
employee-manager db init
```

**Common errors**:
- Command fails silently
- Database created in wrong location
- Schema version mismatch
- Missing indexes

#### Step 5: Customize Application

```python
# User must edit source code or config
APP_TITLE = "Mon Entrepôt - Gestion RH"
APP_THEME = "blue"  # What are options?
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 800
```

**Common errors**:
- Editing source code directly (breaks updates)
- Invalid theme names
- Wrong window dimensions
- Typos in titles

## Real-World Impact

### Scenario 1: Non-Technical Warehouse Manager

**User Profile**:
- Manages 30 employees
- Comfortable with Excel
- Never edited configuration file
- Wants to track CACES certifications

**Experience**:
```
1. Downloads Wareflow EMS
2. Extracts files
3. Reads README: "Configure application"
4. Opens config.py in Notepad
5. Confused by Python syntax
6. Tries to guess values
7. Makes typo: "ALERT_CRITICL_DAYS = 7" (missing A)
8. Application crashes with cryptic error
9. Doesn't know how to debug
10. Gives up, returns to Excel
```

**Result**: Lost customer

### Scenario 2: HR Consultant Deploying to Client

**User Profile**:
- Technical consultant
- Deploying to 5th client this month
- Each client wants different configuration

**Experience**:
```
Client 1: Manually configured (2 hours)
Client 2: Manually configured (2 hours)
Client 3: Copied config from Client 2, forgot to change company name (30 min)
Client 4: Tried to automate with script, script had bugs (3 hours)
Client 5: Tired of manual config, rushes, makes mistakes (1 hour)

Total: 8.5 hours for 5 deployments
Errors: 2 mistakes found later
```

**Result**: Inefficient, error-prone, consultant burns out

### Scenario 3: Small Warehouse Chain

**User Profile**:
- 3 warehouse sites
- Each site needs different configuration
- IT person has basic skills

**Experience**:
```
Site A: Configured by IT person (1 hour)
Site B: Copied config from Site A, forgot to customize roles (30 min)
Site C: Tried to customize, broke configuration (2 hours to fix)

Result:
- Site B has wrong roles (can't add "Réceptionnaire")
- Site C was down for 2 hours
- Inconsistent configurations across sites
```

**Result**: Inconsistent deployments, support burden

## Problems Created

### 1. No Guidance During Setup

**Users are left guessing**:
- What are valid workspace names?
- What roles should I define?
- What contract types exist in French labor law?
- What are reasonable alert thresholds?
- What database filename should I use?

**Impact**:
- Analysis paralysis (can't decide, so don't start)
- Poor configuration choices
- Inconsistent setups

### 2. Error-Prone Manual Editing

**Common mistakes**:
- Syntax errors in Python/JSON/YAML
- Typos in configuration keys
- Wrong data types (string instead of integer)
- Invalid file paths
- Missing required fields

**Impact**:
- 30% of first-time setups fail
- Cryptic error messages
- Users give up

### 3. No Validation

**Configuration accepted without validation**:
```
# User can set:
ALERT_CRITICAL_DAYS = -1  # Invalid (negative)
ALERT_WARNING_DAYS = 5  # Invalid (less than critical)
DATABASE_PATH = "C:\Windows\System32\myfile.db"  # Dangerous location
WORKSPACES = []  # Empty (no workspaces defined)
```

**Impact**:
- Silent failures
- Confusing runtime errors
- Data corruption

### 4. No Defaults or Templates

**Every installation starts from scratch**:
- No sensible defaults
- No industry templates
- No presets for common scenarios
- Must configure everything manually

**Impact**:
- 1-2 hour setup time
- Reinventing the wheel each time
- Inconsistent best practices

### 5. Documentation Burden

**Users must read extensive documentation**:
- Configuration reference (10+ pages)
- French labor law requirements
- CACES categories
- Medical visit types
- Alert best practices

**Impact**:
- High learning curve
- Users skip documentation, make mistakes

### 6. Configuration Drift

**Each deployment differs**:
- Different directory structures
- Different file names
- Different configurations
- Different best practices

**Impact**:
- Impossible to standardize support
- Cannot share documentation
- Cannot automate updates

### 7. No Rollback

**If configuration breaks**:
- No backup of working config
- No way to revert to defaults
- Must reinstall from scratch

**Impact**:
- Fear of customization
- Stuck with bad configurations

## Missing Features

### Interactive Setup Wizard
- [ ] Guided step-by-step configuration
- [ ] Input validation during setup
- [ ] Sensible defaults provided
- [ ] Helpful explanations for each setting
- [ ] Preview before finalizing

### Templates
- [ ] Basic template (single warehouse)
- [ ] Advanced template (multi-site)
- [ ] Industry presets (logistics, retail, manufacturing)
- [ ] Custom template creation

### Configuration Generator
- [ ] Automatically creates config files
- [ ] Validates configuration
- [ ] Creates correct directory structure
- [ ] Initializes database
- [ ] Generates documentation

### Preset Values
- [ ] Common workspaces (Quai, Zone A, Bureau, etc.)
- [ ] Standard roles (Cariste, Magasinier, Préparateur, etc.)
- [ ] French contract types (CDI, CDD, Intérim, etc.)
- [ ] CACES categories (R489-1A, R489-1B, etc.)
- [ ] Medical visit types (initial, periodic, recovery)

## Proposed Solution

### Solution 1: Interactive Setup Wizard

Create a command-line wizard that guides users through configuration:

```bash
$ wems configure

🎯 Wareflow EMS Configuration Wizard
====================================

This wizard will help you configure Wareflow EMS for your company.

[Step 1/7] Company Information
────────────────────────────────
Company name: [Mon Entrepôt SARL]
SIRET (optional): [12345678900012]
Contact email: [contact@mon-entrepot.fr]
Phone (optional): [0102030405]

[Step 2/7] Organization Setup
──────────────────────────────
Workspaces (comma-separated):
  [Quai, Zone A, Zone B, Bureau]
  💡 Common: Quai, Zone A, Zone B, Bureau, Réception, Expédition

Roles (comma-separated):
  [Cariste, Magasinier, Préparateur]
  💡 Common: Cariste, Magasinier, Préparateur, Réceptionnaire, Expéditeur

Contract types (comma-separated):
  [CDI, CDD, Intérim, Alternance, Stage]

[Step 3/7] Alert Configuration
──────────────────────────────
Critical alert threshold (days): [7]
  💡 Alert when CACES/visits expire within 7 days

Warning alert threshold (days): [30]
  💡 Alert when CACES/visits expire within 30 days

Info alert threshold (days): [90]
  💡 Alert when CACES/visits expire within 90 days

[Step 4/7] Database Configuration
─────────────────────────────────
Database filename: [employee_manager.db]
Backup retention (days): [30]
Enable automatic backups: [Yes]

[Step 5/7] Interface Customization
───────────────────────────────────
Window title: [Mon Entrepôt - Gestion RH]
Theme: [System] (Light, Dark, System)
Color theme: [blue] (blue, green, dark-blue)
Language: [Français]

[Step 6/7] Advanced Features
─────────────────────────────
Enable multi-site support: [No]
Enable audit trail: [No]
Enable API access: [No]

[Step 7/7] Review & Confirm
────────────────────────────
Company: Mon Entrepôt SARL
Workspaces: Quai, Zone A, Zone B, Bureau (4)
Roles: Cariste, Magasinier, Préparateur (3)
Alerts: Critical=7d, Warning=30d, Info=90d
Database: employee_manager.db
Backups: Enabled (30 days retention)

Configuration looks correct? [Yes/No]: Yes

✅ Configuration saved to config.yaml
✅ Directory structure created
✅ Database initialized
✅ Ready to use!

Start application with: wems start
```

**Benefits**:
- No manual file editing
- Validation during input
- Helpful hints and defaults
- Clear progress indication
- Confidence that config is correct

### Solution 2: Template System

Provide pre-configured templates for common scenarios:

**Basic Template** (default):
```yaml
# Single warehouse, basic setup
organization:
  company:
    name: "My Warehouse"
  workspaces: ["Quai", "Zone A", "Zone B"]
  roles: ["Cariste", "Magasinier", "Préparateur"]
  contract_types: ["CDI", "CDD", "Intérim"]

alerts:
  critical_days: 7
  warning_days: 30
  info_days: 90
```

**Advanced Template**:
```yaml
# Multi-site, advanced features
organization:
  workspaces:
    - Site A - Quai
    - Site A - Zone A
    - Site B - Quai
    - Site B - Zone B
  roles:
    - Cariste
    - Magasinier
    - Préparateur
    - Réceptionnaire
    - Expéditeur
    - Chef d'équipe

alerts:
  critical_days: 7
  warning_days: 30
  info_days: 90

advanced:
  multi_site:
    enabled: true
    sites: ["Site A", "Site B"]
```

**Industry Presets**:

**Logistics Preset**:
```yaml
organization:
  workspaces: [Quai, Réception, Expédition, Zone A, Zone B]
  roles: [Cariste, Magasinier, Préparateur de commandes, Réceptionnaire]
```

**Retail Warehouse Preset**:
```yaml
organization:
  workspaces: [Rayon A, Rayon B, Réserve, Stockage]
  roles: [Magasinier, Préparateur, Chef de rayon]
```

**Manufacturing Preset**:
```yaml
organization:
  workspaces: [Ligne 1, Ligne 2, Entrepôt, Expédition]
  roles: [Opérateur, Magasinier, Cariste, Chef d'équipe]
```

**Benefits**:
- 80% of companies can use preset
- Only 20% need customization
- Faster deployment
- Industry best practices built-in

### Solution 3: Configuration Generator

Command to generate configuration:

```bash
# Generate with defaults
wems config init --defaults

# Generate with template
wems config init --template advanced

# Generate with preset
wems config init --preset logistics

# Generate interactively
wems config init --interactive

# Generate with custom values
wems config init \
  --company "Mon Entrepôt SARL" \
  --workspaces "Quai,Zone A,Bureau" \
  --roles "Cariste,Magasinier"
```

**Benefits**:
- Command-line friendly
- Automatable
- Can be scripted
- Reproducible configurations

## Implementation Plan

### Phase 1: Wizard Framework (1 week)
1. Create `src/bootstrapper/wizard.py`
2. Implement step-by-step interface
3. Add input validation
4. Add progress indicators
5. Add helpful hints

### Phase 2: Question Types (3 days)
1. Text input
2. Number input (with validation)
3. Multi-select (workspaces, roles)
4. Yes/No questions
5. File/directory paths
6. Email/phone validation

### Phase 3: Template System (1 week)
1. Create template structure
2. Basic template
3. Advanced template
4. Industry presets
5. Template validation

### Phase 4: Configuration Generator (3 days)
1. Create `src/bootstrapper/config_generator.py`
2. Implement `wems config init` command
3. Template loading
4. YAML generation
5. Validation

### Phase 5: Integration (2 days)
1. Integrate wizard with bootstrapper
2. Add to `wems init` command
3. Test end-to-end flow
4. Documentation

## Files to Create

- `src/bootstrapper/wizard.py`
- `src/bootstrapper/config_generator.py`
- `src/bootstrapper/templates.py`
- `src/cli/config.py`
- `assets/templates/basic/config.yaml`
- `assets/templates/advanced/config.yaml`
- `assets/presets/logistics.yaml`
- `assets/presets/retail.yaml`
- `assets/presets/manufacturing.yaml`
- `schemas/config_schema.json`

## Files to Modify

- `src/bootstrapper/init_command.py` - Integrate wizard
- `src/utils/config.py` - Support YAML config

## Dependencies to Add

```toml
[project.dependencies]
"questionary>=2.0.0"  # Interactive CLI prompts
"pyyaml>=6.0"         # YAML configuration
"jsonschema>=4.0"     # Schema validation
```

## Testing Requirements

- Test wizard with all inputs
- Test validation catches invalid inputs
- Test templates load correctly
- Test presets apply correctly
- Test config generation
- Test user can go back and change answers
- Test user can cancel and restart
- Test confirmation step shows correct summary
- Test config.yaml is valid YAML
- Test generated config passes schema validation

## Benefits

### For End Users
- **Ease**: No manual file editing
- **Speed**: Setup in 5 minutes instead of 1-2 hours
- **Confidence**: Validation ensures config is correct
- **Guidance**: Helpful hints and explanations

### For Consultants
- **Efficiency**: Deploy clients in 5 minutes
- **Consistency**: Templates ensure identical setups
- **Customization**: Still flexible for special cases
- **Professionalism**: Impresses clients with smooth setup

### For Business
- **Adoption**: Lower barrier to entry
- **Support**: 80% fewer configuration issues
- **Scalability**: Can deploy to many clients quickly
- **Quality**: Validated configurations reduce bugs

## Success Metrics

- [ ] Setup time reduced from 1-2 hours to 5 minutes
- [ ] Configuration error rate reduced from 30% to <5%
- [ ] User satisfaction score > 4.5/5 for setup experience
- [ ] 80% of users can use templates without customization
- [ ] Zero manual file editing required

## Related Issues

- #026: Multi-Company Deployment Requires Manual Reinstallation (wizard is part of bootstrapper)
- #027: Application Requires Python Runtime Installation (setup wizard part of bootstrapper)

## Priority

**HIGH** - Significantly improves user experience, reduces support burden

## Estimated Effort

3 weeks (wizard + templates + generator + integration)

## Mitigation

While waiting for wizard:
1. Provide configuration templates in documentation
2. Create setup script with default values
3. Add extensive validation and error messages
4. Create video tutorials for configuration
5. Offer pre-configured virtual machines or containers
