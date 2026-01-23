# [HIGH] Multi-Company Deployment Requires Manual Reinstallation

## Type
**Deployment / Scalability**

## Severity
**HIGH** - Blocks efficient multi-client deployment, limits business scalability

## Affected Components
- **Deployment Process** - Entire installation workflow
- **Configuration** - Per-company settings
- **Database** - Isolated data per company

## Description

Deploying the Wareflow EMS application for multiple companies currently requires completely manual processes for each installation. HR consultants, system integrators, and IT service providers who manage multiple client installations cannot efficiently scale their operations.

### Current Deployment Process

For each new company, consultants must:
1. Copy entire source code directory
2. Reinstall Python dependencies (`uv sync` or `pip install`)
3. Manually create directory structure (`data/`, `documents/`, `backups/`)
4. Edit configuration files by hand
5. Initialize database schema
6. Configure company-specific settings (roles, workspaces, alerts)
7. Test the installation
8. Create desktop shortcuts
9. Document the installation

**Time required**: 1-2 hours per company

**Scalability problem**:
- Managing 5 companies = 5-10 hours of setup time
- Managing 20 companies = 20-40 hours of setup time
- Each company update requires repeating this process

### Real-World Impact

**Scenario 1: HR Consultant with 10 Clients**
```
Month 1: Deploy to 3 new clients (3-6 hours work)
Month 2: Bug fix requires updating all 10 clients (10-20 hours)
Month 3: Each client wants custom configuration (10-20 hours)
Month 4: New feature requires redeployment to all 10 clients (10-20 hours)

Total time spent on deployment: 33-66 hours (instead of focusing on client work)
```

**Scenario 2: IT Service Provider**
- Wants to deploy to 50 warehouse clients
- Cannot scale deployment process
- Must hire more staff just to handle installations
- Becomes bottleneck to business growth

**Scenario 3: Single Company with Multiple Sites**
- Warehouse company with 5 different sites
- Each site needs isolated data and configuration
- Current process requires 5 separate full installations
- No centralized management

## Problems Created

### 1. No Multi-Tenancy
Each installation is completely independent:
- Separate source code copies (waste of disk space)
- Separate dependency installations (waste of time)
- Separate update processes (maintenance nightmare)
- No centralized management

### 2. Configuration Drift
Each manually configured installation differs:
- Inconsistent directory structures
- Inconsistent database schemas
- Incompatible configurations
- Impossible to standardize support

### 3. Update Burden
When bugs are fixed or features added:
- Must update each installation individually
- No automatic update mechanism
- Risk of some installations being outdated
- Testing burden multiplies by number of installations

### 4. Error-Prone Manual Process
Manual steps lead to:
- Missed configuration steps
- Incorrect file permissions
- Incompatible dependencies
- Database initialization failures
- Hard-to-reproduce issues

### 5. No Isolation Between Companies
Current limitations:
- All installations share same application code
- Difficult to maintain different versions per client
- Risk of breaking all clients with one update
- Cannot rollback per-client if issues occur

## Missing Features

### Application Generator
- [ ] Command to create new company instance (`wems init <company>`)
- [ ] Interactive setup wizard
- [ ] Automatic directory structure creation
- [ ] Database initialization
- [ ] Configuration file generation
- [ ] Company-specific customization

### Template System
- [ ] Pre-configured templates for common industries
- [ ] Basic template (single warehouse)
- [ ] Advanced template (multi-site)
- [ ] Enterprise template (multi-company)
- [ ] Custom template creation

### Isolation
- [ ] Separate database per company
- [ ] Separate document storage per company
- [ ] Separate configuration per company
- [ ] Independent backup per company
- [ ] Version-specific instances

### Management Tools
- [ ] List all company instances
- [ ] Update specific instance
- [ ] Update all instances
- [ ] Migrate instances
- [ ] Delete instances

## Proposed Solution

### Solution 1: Application Generator (Bootstrapper)

Create a command-line tool that generates complete, isolated application instances:

```bash
# Generate new company instance
wems init "Warehouse ABC"

# Creates:
warehouse-abc/
├── wems.exe                    # Pre-compiled executable
├── config.yaml                # Company-specific config
├── data/
│   └── warehouse_abc.db       # Isolated database
├── documents/                 # Isolated document storage
│   ├── caces/
│   ├── medical/
│   └── training/
├── backups/                   # Company-specific backups
├── logs/                      # Company-specific logs
└── README.md                  # Generated documentation
```

**Benefits**:
- 5-minute deployment instead of 1-2 hours
- Consistent installations every time
- No manual steps
- No dependencies to install
- Isolated data and configuration

### Solution 2: Interactive Setup Wizard

Guided setup for company-specific configuration:

```bash
$ wems init "Mon Entrepôt SARL"

🎉 Wareflow EMS Setup
====================

[1/7] Company Information
├─ SIRET: [12345678900012]
├─ Email: [contact@mon-entrepot.fr]
├─ Phone: [0102030405]
└─ Address: [123 Rue de la Logistique]

[2/7] Organization Setup
├─ Workspaces: [Quai, Zone A, Zone B]
├─ Roles: [Cariste, Magasinier, Préparateur]
└─ Contract Types: [CDI, CDD, Intérim]

[3/7] Alert Configuration
├─ Critical threshold: [7] days
├─ Warning threshold: [30] days
└─ Alert recipient: [manager@mon-entrepot.fr]

✅ Application created successfully!
```

**Benefits**:
- No manual file editing
- Validation during setup
- User-friendly interface
- No documentation needed to get started

### Solution 3: Template System

Pre-configured templates for common scenarios:

**Basic Template** (default):
- Single workspace
- 3 roles (Cariste, Magasinier, Préparateur)
- Basic CACES tracking
- Medical visit tracking

**Advanced Template**:
- Multiple workspaces
- Custom roles
- Advanced reporting
- Excel import/export

**Enterprise Template**:
- Multi-site support
- Advanced permissions
- Audit trail
- API access

**Industry Presets**:
- Logistics preset
- Retail warehouse preset
- Manufacturing preset

**Benefits**:
- 80% of companies can use presets
- Customization only for remaining 20%
- Faster deployment
- Best practices built-in

### Solution 4: Instance Management

CLI commands to manage multiple instances:

```bash
# List all instances
wems instance list

# Update specific instance
wems instance update --path "C:/apps/warehouse-abc"

# Update all instances
wems instance update --all

# Migrate instance to new version
wems instance migrate --path "C:/apps/warehouse-abc" --to-version "2.0.0"

# Delete instance
wems instance delete --path "C:/apps/warehouse-abc"
```

**Benefits**:
- Centralized management
- Batch operations
- Version control per instance
- Safe deletion with backup

## Implementation Plan

### Phase 1: Core Generator (1 week)
1. Create `src/bootstrapper/init_command.py`
2. Implement `wems init` command
3. Directory structure creation
4. Database initialization
5. Basic config.yaml generation

### Phase 2: Interactive Wizard (1 week)
1. Create `src/bootstrapper/wizard.py`
2. Step-by-step setup interface
3. Input validation
4. Progress indicators
5. Confirmation and review

### Phase 3: Template System (1 week)
1. Create template structure (`assets/templates/`)
2. Basic template
3. Advanced template
4. Enterprise template
5. Industry presets
6. Template validation

### Phase 4: Management Tools (3 days)
1. Instance listing
2. Instance update commands
3. Instance migration
4. Instance deletion
5. Batch operations

## Files to Create

- `src/bootstrapper/__init__.py`
- `src/bootstrapper/init_command.py`
- `src/bootstrapper/wizard.py`
- `src/bootstrapper/config_generator.py`
- `src/bootstrapper/template_engine.py`
- `src/bootstrapper/instance_manager.py`
- `src/cli/init.py`
- `src/cli/instance.py`
- `assets/templates/basic/config.yaml`
- `assets/templates/advanced/config.yaml`
- `assets/templates/enterprise/config.yaml`
- `assets/presets/logistics.yaml`
- `assets/presets/retail.yaml`
- `tests/test_bootstrapper/test_init.py`
- `tests/test_bootstrapper/test_wizard.py`
- `tests/test_bootstrapper/test_templates.py`

## Files to Modify

- `src/cli/__init__.py` - Add init and instance commands
- `pyproject.toml` - Add entry points
- `README.md` - Document bootstrapper usage

## Dependencies to Add

```toml
[project.dependencies]
"questionary>=2.0.0"  # Interactive CLI prompts
"pyyaml>=6.0"         # YAML configuration
"jsonschema>=4.0"     # Schema validation
```

## Testing Requirements

- Test basic `wems init` command
- Test interactive wizard with all inputs
- Test template generation (basic, advanced, enterprise)
- Test custom directory path
- Test invalid company names
- Test existing directory detection
- Test database initialization
- Test config.yaml generation
- Test instance listing
- Test instance update
- Test instance deletion
- Test batch operations

## User Benefits

### For Consultants
- **Efficiency**: Deploy new client in 5 minutes vs 1-2 hours
- **Scalability**: Manage 50+ clients without hiring more staff
- **Consistency**: All installations configured identically
- **Professionalism**: Branded apps per client

### For End Users
- **Simplicity**: No technical knowledge required
- **Speed**: Start using app immediately after setup
- **Isolation**: Each company has independent data
- **Customization**: Company-specific configuration

### For Business
- **Revenue**: Can charge setup + maintenance fees
- **Growth**: No bottleneck to client acquisition
- **Margin**: Less time per installation = higher margin
- **Competitive**: Faster deployment than competitors

## Success Metrics

- [ ] Deployment time reduced from 1-2 hours to 5 minutes
- [ ] 95% reduction in deployment errors
- [ ] Ability to manage 50+ instances efficiently
- [ ] User satisfaction score > 4.5/5
- [ ] Support requests reduced by 80%

## Related Issues

- #002: Application Requires Python Runtime Installation (solved by bootstrapper)
- #003: Each Installation Requires Manual Configuration (solved by wizard)
- #010: No Migration Path from Existing Installations (related)

## Priority

**HIGH** - Enables business scaling, critical for consultant use case

## Estimated Effort

3 weeks (core generator + wizard + templates + management)

## Mitigation

While waiting for bootstrapper implementation:
1. Create deployment script to automate manual steps
2. Document deployment checklist
3. Create configuration templates manually
4. Use Docker for containerized deployments
5. Offer professional installation services
