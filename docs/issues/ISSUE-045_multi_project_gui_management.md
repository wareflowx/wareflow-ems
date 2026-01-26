# [HIGH] No Multi-Project Management from GUI

## Type
**Feature / Usability**

## Severity
**HIGH** - Blocks multi-company usage, limits scalability for consultants and power users

## Affected Components
- **User Interface** - No project selection screen
- **Application Architecture** - Single-database design
- **Database Layer** - No project registry or isolation
- **Configuration** - Global settings, not per-project
- **Backup System** - No per-project backup isolation

## Description

Wareflow EMS currently manages a single company/project per installation. Users cannot create, open, or switch between multiple projects from the GUI, making it unsuitable for consultants, multi-company organizations, or multi-site deployments.

### Current Limitations

**Single Database Design**:
- Application is hardcoded to use one database file
- Configuration points to single `data/employee_manager.db`
- No way to switch databases from GUI
- No project metadata or organization

**User Experience**:
```
First launch:
→ App opens directly to empty dashboard
→ User sees "No employees found"
→ User assumes this is for "their company"

Reality:
→ This single database IS their company
→ Can't create separate database for new company
→ Can't switch between companies
→ Must reinstall entire app for new company
```

**Multi-Company Scenarios Blocked**:

**Scenario 1: HR Consultant with 10 Clients**
```
Consultant wants to manage 10 different client companies

Current requirement:
- 10 separate installations of app
- 10 separate Python environments
- 10 separate data directories
- Must remember which installation is for which client
- Must manually switch between installations
- Can't easily compare data across clients

Time spent: 2-3 hours switching contexts per week
```

**Scenario 2: Multi-Site Warehouse Company**
```
Company: Logistics France SA
Sites: Paris, Lyon, Marseille, Lille, Bordeaux

Current requirement:
- Choose: One database for all sites (mixed data, confusing)
- OR: 5 separate installations (no centralized management)
- No way to see company-wide metrics
- No way to transfer employees between sites
- No way to consolidate reports

Problems:
- Site managers can't see other site data (security)
- HQ can't see all sites in one view (reporting)
- Employee transfers require export/import (manual)
```

**Scenario 3: Holding Company with Subsidiaries**
```
Holding company: Warehouse Group
Subsidiaries:
- Logistics Paris SAS
- Storage Lyon SARL
- Distribution Marseille

Current requirement:
- One database = mixed companies (confusing)
- OR separate installations = no consolidated view
- Can't run company-wide reports
- Can't consolidate employee data
- Can't manage subsidiaries independently
```

### Real-World Impact

**User Story: Consultant Marie**
```
Marie is an HR consultant with 8 clients

Monday:
- Client A (Warehouse ABC): Opens app, views employees
- Need to switch to Client B: Must close app, open different installation
- Client B: Opens app from C:\Clients\WarehouseB\wareflow-ems
- Client C: Opens app from C:\Clients\WarehouseC\wareflow-ems
- ...

Problems:
- 8 desktop shortcuts (clutter)
- 8 separate installations to update
- 8 separate databases to backup
- Can't remember which installation is which client
- Sometimes opens wrong client's data (embarrassing!)

Time wasted: 1-2 hours per week switching contexts
```

**User Story: Multi-Site Manager Jean**
```
Jean manages 5 warehouse sites for LogisticsPro Inc.

Current situation:
- One database per site requirement
- Must open 5 different apps to see all sites
- Can't see consolidated view of all employees
- Can't see company-wide compliance metrics
- Employee transfer: Export from Site A, import to Site B

Pain points:
- Monthly reports: 5x the work (5 separate reports)
- Compliance overview: Must check 5 apps separately
- Employee transfer: 30+ minutes of manual work
- No audit trail of transfers

Time wasted: 3-4 hours per month on manual consolidation
```

## Problems Created

### 1. No Project Isolation
**Current limitation**: All data in single database
- Cannot separate data by company/site
- Cannot manage independent employee sets
- Cannot have different configurations per company
- Security risk: all data accessible to all users

**Example**:
```
Consultant with clients A and B:
- If single DB: Sees both clients' data mixed together
- If separate installations: Must manually switch
- No way to say "Show me only Client A's employees"
- No way to say "Show me compliance for all clients"
```

### 2. No GUI for Project Management
**Current limitation**: All project management via CLI or file system
- Cannot create project from GUI
- Cannot delete project from GUI
- Cannot rename project from GUI
- Cannot switch projects from GUI
- Must edit config files or reinstall

**User friction**:
```
User wants to create new company database
Current options:
1. Edit config.json (technical, error-prone)
2. Reinstall app (time-consuming)
3. Manually copy/rename database file (confusing)
4. Use CLI commands (non-technical users can't)

All options require technical knowledge
All options are error-prone
```

### 3. No Project Metadata
**Current limitation**: No information about projects
- Cannot see when project was created
- Cannot see when project was last opened
- Cannot add description or notes
- Cannot tag or categorize projects
- Difficult to identify projects

**Example**:
```
User has databases:
- employee_manager.db (old)
- employee_manager2.db (newer)
- employee_manager_copy.db (backup?)
- employee_manager_final.db (current?)

Questions:
- Which is which?
- Which is current?
- Can I delete the old ones?
- What's the difference between them?

User is afraid to delete anything (keeps all copies)
```

### 4. No Per-Project Configuration
**Current limitation**: Global configuration for all projects
- Alert thresholds apply to all projects
- Role definitions apply to all projects
- Workspace definitions apply to all projects
- Cannot customize per company

**Real-world impact**:
```
Client A wants:
- 30-day warning threshold
- Roles: Cariste, Magasinier
- Workspaces: Quai A, Quai B

Client B wants:
- 60-day warning threshold
- Roles: Préparateur, Dispatcher
- Workspaces: Zone 1, Zone 2, Zone 3

Current: Impossible! Must use same config for both
Workaround: Use separate installations (back to problem 1)
```

### 5. No Centralized Project Management
**Current limitation**: No registry or catalog of projects
- Cannot list all projects
- Cannot search projects
- Cannot see project statistics
- Cannot see storage usage
- Cannot see last backup date

**Management burden**:
```
Consultant with 15 clients:
- Forgets which clients are active
- Doesn't know which DBs are safe to delete
- Can't see which clients haven't been opened in 6 months
- Can't see storage usage per client
- No overview of practice
```

### 6. Backup and Restore Complexity
**Current limitation**: Backups not isolated by project
- All backups mixed together
- Difficult to find specific project's backup
- Risk of restoring wrong backup
- No per-project backup retention policies

**Example**:
```
Backups directory:
backups/
  - backup_20250101_120000.db
  - backup_20250102_080000.db
  - backup_20250103_150000.db
  - ... (hundreds of files)

Question: Which backup is for which project?
Answer: Can't tell from filename!
Risk: Restore wrong client's data → disaster
```

## Missing Features

### Project Registry
- [ ] Central registry database (projects.db)
- [ ] Project metadata (name, description, created_at, last_opened)
- [ ] Project storage location tracking
- [ ] Project status (active, archived, deleted)

### Project Management GUI
- [ ] Project Selector screen on startup
- [ ] Create new project wizard
- [ ] Open existing project
- [ ] Delete project with confirmation
- [ ] Rename project
- [ ] Archive inactive projects

### Per-Project Configuration
- [ ] Isolated config files per project
- [ ] Project-specific alert thresholds
- [ ] Project-specific roles and workspaces
- [ ] Project-specific backup settings

### Per-Project Data Isolation
- [ ] Separate database file per project
- [ ] Separate document storage per project
- [ ] Separate backup directory per project
- [ ] Separate log files per project

### Project Switching
- [ ] Close current project
- [ ] Open different project
- [ ] Confirm unsaved changes before switch
- [ ] Remember last opened project

### Project Management CLI
- [ ] `wems project list` - List all projects
- [ ] `wems project create <name>` - Create new project
- [ ] `wems project delete <name>` - Delete project
- [ ] `wems project info <name>` - Show project details

## Proposed Solution

### Solution 1: Project Registry Database

Create `projects/registry.db` to track all projects:

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    db_path TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_opened_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    storage_size_mb INTEGER,
    employee_count INTEGER,
    config_json TEXT
);

CREATE INDEX idx_projects_slug ON projects(slug);
CREATE INDEX idx_projects_active ON projects(is_active);
CREATE INDEX idx_projects_last_opened ON projects(last_opened_at);
```

**Project Structure**:
```
projects/
├── registry.db                    # Project catalog
├── client-abc-warehouse/
│   ├── employee_manager.db       # Project database
│   ├── config.json               # Project config
│   ├── documents/
│   │   ├── caces/
│   │   ├── medical/
│   │   └── training/
│   ├── backups/
│   │   └── auto_*.db
│   └── logs/
├── client-xyz-logistics/
│   ├── employee_manager.db
│   ├── config.json
│   └── ...
└── archived/
    └── old-client-2023/
        └── ...
```

### Solution 2: Project Selector GUI

Create startup screen for project management:

**UI Layout**:
```
┌─────────────────────────────────────────────────┐
│  🏢 Wareflow EMS - Project Manager              │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Search projects...]            [+ New Project]│
│                                                 │
│  Recent Projects:                               │
│  ┌─────────────────────────────────────────┐   │
│  │ 📦 Client ABC - Warehouse               │   │
│  │    Last opened: 2 hours ago             │   │
│  │    45 employees • 3 alerts              │   │
│  │    [Open]  [Settings]                   │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │ 📦 Client XYZ - Logistics               │   │
│  │    Last opened: Yesterday               │   │
│  │    128 employees • 12 alerts            │   │
│  │    [Open]  [Settings]                   │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  All Projects (12)                    [Show All]│
│                                                 │
│  [•] Show archived projects                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Features**:
- List of all projects with metadata
- Search and filter projects
- Last opened project highlighted
- Project statistics (employee count, alerts)
- Quick actions (Open, Settings, Delete, Archive)
- Create new project button

### Solution 3: Create Project Wizard

Step-by-step project creation:

```
Step 1: Basic Information
┌─────────────────────────────────────┐
│  Create New Project                 │
├─────────────────────────────────────┤
│  Project Name:                      │
│  [My Warehouse                ]    │
│                                     │
│  Description (optional):            │
│  [Main warehouse facility     ]    │
│                                     │
│  Project Icon:                      │
│  [📦] [🏭] [🏢] [🏗️] [📊]           │
│                                     │
│           [Back]        [Next →]    │
└─────────────────────────────────────┘

Step 2: Configuration
┌─────────────────────────────────────┐
│  Create New Project - Configuration │
├─────────────────────────────────────┤
│  Workspaces (one per line):         │
│  [Quai A                     ] [+]  │
│  [Quai B                     ] [+]  │
│  [Zone Stockage              ] [+]  │
│                                     │
│  Employee Roles (one per line):     │
│  [Cariste                    ] [+]  │
│  [Magasinier                 ] [+]  │
│  [Préparateur de commandes   ] [+]  │
│                                     │
│  Alert Threshold:                   │
│  (○) 30 days  (•) 60 days  (○) 90   │
│                                     │
│           [← Back]       [Next →]   │
└─────────────────────────────────────┘

Step 3: Review & Create
┌─────────────────────────────────────┐
│  Create New Project - Review        │
├─────────────────────────────────────┤
│  Project: My Warehouse              │
│  Description: Main warehouse        │
│  Icon: 📦                           │
│                                     │
│  Workspaces: 3                      │
│  • Quai A                           │
│  • Quai B                           │
│  • Zone Stockage                    │
│                                     │
│  Roles: 3                           │
│  • Cariste                          │
│  • Magasinier                       │
│  • Préparateur de commandes         │
│                                     │
│  Location:                          │
│  projects/my-warehouse/             │
│                                     │
│  Storage: ~5 MB estimated           │
│                                     │
│           [← Back]  [Create]       │
└─────────────────────────────────────┘
```

### Solution 4: Per-Project Configuration

Isolated configuration per project:

```json
// projects/client-abc/config.json
{
  "project": {
    "name": "Client ABC - Warehouse",
    "slug": "client-abc",
    "created_at": "2025-01-26T10:00:00Z",
    "version": "1.0.0"
  },
  "organization": {
    "workspaces": ["Quai A", "Quai B", "Zone Stockage"],
    "roles": ["Cariste", "Magasinier", "Préparateur"],
    "contract_types": ["CDI", "CDD", "Intérim"]
  },
  "alerts": {
    "critical_days": 7,
    "warning_days": 30,
    "info_days": 90
  },
  "backup": {
    "enabled": true,
    "max_backups": 30,
    "auto_backup_on_startup": true
  },
  "ui": {
    "theme": "blue",
    "mode": "system",
    "default_view": "dashboard"
  }
}
```

### Solution 5: Dynamic Database Connection

Modify database layer to support project switching:

```python
# src/project/project_manager.py
class ProjectManager:
    def list_projects(self) -> List[Project]:
        """List all projects from registry"""

    def create_project(self, name: str, config: dict) -> Project:
        """Create new project with database"""

    def open_project(self, project_id: int) -> Project:
        """Open project and load database"""

    def close_project(self):
        """Close current project database"""

    def delete_project(self, project_id: int):
        """Delete project and all data"""

# src/database/connection.py (modified)
def connect_to_project(project: Project):
    """Connect to specific project database"""
    db_path = project.db_path
    database.init(db_path)
    database.connect()
```

### Solution 6: Application Startup Flow

```
Application Launch
    ↓
Check if registry.db exists
    ↓
    No → Create registry, show welcome wizard
    Yes → Open project selector
    ↓
User selects or creates project
    ↓
Connect to project database
    ↓
Run migrations if needed
    ↓
Create startup backup
    ↓
Open MainWindow with project data
    ↓
User works with project
    ↓
User closes or switches project
    ↓
Update last_opened_at in registry
    ↓
Return to project selector or exit
```

## Implementation Plan

### Phase 1: Project Registry (2 days)
1. Create `src/project/models.py` with Project model
2. Create `projects/registry.db` schema
3. Create `src/project/project_manager.py` with CRUD operations
4. Implement project listing
5. Implement project creation
6. Implement project deletion
7. Add tests

### Phase 2: Project Selector GUI (3 days)
1. Create `src/ui_ctk/views/project_selector_view.py`
2. Design project card layout
3. Implement project list
4. Add search and filter
5. Add project statistics
6. Implement project switching
7. Handle edge cases (no projects, first launch)
8. Add tests

### Phase 3: Create Project Wizard (2 days)
1. Create `src/ui_ctk/forms/project_wizard.py`
2. Implement multi-step wizard
3. Add validation
4. Add configuration customization
5. Implement project creation
6. Add tests

### Phase 4: Dynamic Database Connection (2 days)
1. Modify `src/database/connection.py`
2. Add `connect_to_project()` function
3. Handle project switching
4. Handle database closure
5. Update all database access code
6. Add tests

### Phase 5: Per-Project Configuration (2 days)
1. Modify `utils/config.py` for project-specific config
2. Add default config generation
3. Implement config loading per project
4. Implement config saving per project
5. Update config-dependent code
6. Add tests

### Phase 6: Backup Integration (1 day)
1. Modify `utils/backup_manager.py`
2. Add per-project backup directories
3. Update backup creation logic
4. Update restore logic
5. Add tests

### Phase 7: Migration from Single-Project (1 day)
1. Detect existing single-project setup
2. Offer migration to multi-project system
3. Migrate existing database to `projects/default/`
4. Migrate existing configuration
5. Create registry entry
6. Test migration

## Files to Create

- `src/project/__init__.py`
- `src/project/models.py` - Project model for registry
- `src/project/project_manager.py` - Project CRUD operations
- `src/project/exceptions.py` - Project-specific exceptions
- `src/ui_ctk/views/project_selector_view.py` - Project selection screen
- `src/ui_ctk/forms/project_wizard.py` - Project creation wizard
- `src/ui_ctk/forms/project_settings_form.py` - Project settings
- `tests/test_project/test_models.py`
- `tests/test_project/test_manager.py`
- `tests/test_project/test_selector_view.py`
- `tests/test_project/test_wizard.py`

## Files to Modify

- `src/main.py` - Add project selector startup
- `src/ui_ctk/app.py` - Support project switching
- `src/database/connection.py` - Add dynamic connection
- `utils/config.py` - Support per-project config
- `utils/backup_manager.py` - Support per-project backups
- `src/lock/models.py` - Per-project locking
- `src/cli/project.py` - Add project management CLI commands
- `README.md` - Document multi-project usage
- `docs/multi-project-guide.md` - User guide for multi-project

## Database Migration Required

New migration: `20250126_140000_add_project_system`

```python
def upgrade():
    """Create project registry system"""
    # Create projects/ directory
    # Create registry.db with projects table
    # Migrate existing installation to 'default' project

def downgrade():
    """Remove project registry"""
    # Keep projects/ for safety
    # Document manual removal process
```

## Testing Requirements

### Test Project Registry
- [ ] Create project in registry
- [ ] List all projects
- [ ] Get project by ID
- [ ] Update project metadata
- [ ] Delete project (cascade)
- [ ] Search projects by name
- [ ] Filter active/archived projects

### Test Project Manager
- [ ] Create new project with database
- [ ] Open existing project
- [ ] Switch between projects
- [ ] Close project
- [ ] Delete project and files
- [ ] Archive project
- [ ] Get project statistics

### Test Project Selector GUI
- [ ] Display project list
- [ ] Search projects
- [ ] Filter projects
- [ ] Open project
- [ ] Delete project with confirmation
- [ ] Create new project from selector
- [ ] Handle no projects case
- [ ] Handle first launch

### Test Create Project Wizard
- [ ] Create project with default config
- [ ] Create project with custom config
- [ ] Validate project name (unique, no special chars)
- [ ] Add workspaces
- [ ] Add roles
- [ ] Set alert thresholds
- [ ] Review before creation
- [ ] Cancel creation

### Test Database Switching
- [ ] Switch from project A to project B
- [ ] Verify correct database loaded
- [ ] Verify data isolation
- [ ] Switch with unsaved changes (prompt)
- [ ] Close and reopen (remembers last project)

### Test Migration from Single-Project
- [ ] Detect existing single-project setup
- [ ] Offer migration option
- [ ] Migrate database successfully
- [ ] Migrate configuration successfully
- [ ] Create registry entry
- [ ] Verify app works after migration

## User Benefits

### For Consultants
- **Efficiency**: Switch between clients in 2 clicks vs 2 minutes
- **Organization**: All clients in one app, not 10+ installations
- **Professionalism**: Branded projects per client
- **Scalability**: Manage 50+ clients easily

### For Multi-Site Companies
- **Centralization**: One app for all sites
- **Isolation**: Separate databases per site
- **Reporting**: Company-wide consolidated reports
- **Transfers**: Easy employee transfers between sites

### For Power Users
- **Flexibility**: Separate projects for different needs
- **Organization**: Group related data
- **Security**: Isolated sensitive projects
- **Control**: Per-project configuration

## Success Metrics

- [ ] Project creation time < 2 minutes
- [ ] Project switching time < 3 seconds
- [ ] 100% data isolation between projects
- [ ] Zero data leakage between projects
- [ ] Migration from single-project < 5 minutes
- [ ] User satisfaction > 4.5/5

## Related Issues

- #026: Multi-Company Deployment Requires Manual Reinstallation (solved by this)
- #036: No Migration Path from Existing Installations (related, for migration)
- #006: Hardcoded Database Path (solved by dynamic connection)

## Priority

**HIGH** - Critical for consultants and multi-site companies, major scalability blocker

## Estimated Effort

2 weeks (registry + selector + wizard + dynamic connection + config + migration)

## Mitigation

While waiting for multi-project GUI:
1. Use separate installations (current workaround)
2. Document manual project switching
3. Provide scripts for project creation
4. Use symbolic links to separate databases
5. Offer professional setup services

## Example User Flow (After Implementation)

```
Launch Wareflow EMS
    ↓
Project Selector Screen
    ↓
Click "+ New Project"
    ↓
Wizard: Step 1 - Enter "Client ABC"
    ↓
Wizard: Step 2 - Configure workspaces and roles
    ↓
Wizard: Step 3 - Review and create
    ↓
Project created in 2 minutes
    ↓
Project opens automatically
    ↓
Work with Client ABC employees
    ↓
Click "Projects" → "Switch Project"
    ↓
Select "Client XYZ"
    ↓
Client XYZ opens in 3 seconds
    ↓
Work with Client XYZ employees

Total time: 5 minutes (vs current 2+ hours for separate installation)
```
