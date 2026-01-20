# CUSTOMTKINTER UI DEVELOPMENT PLAN

## 📋 PLAN STRUCTURE

This plan divides development into **7 sequential phases**, each with clear objectives and specific deliverables.

**Total estimated time**: 5-7 development days

---

## 🎯 PHASE 0: PREPARATION & VALIDATION

### Objectives
- Validate technical stack
- Verify dependencies
- Prepare environment

### Tasks

#### 0.1. Technical Stack
**Tools to use:**
- **UI Framework**: CustomTkinter (modern, native look)
- **ORM**: Peewee (already in place)
- **Database**: SQLite (already in place)
- **Excel Import**: openpyxl (already in pyproject.toml)
- **Build**: PyInstaller (to be added)

**Why CustomTkinter?**
- Modern look (native dark mode)
- Ready-to-use widgets
- Cross-platform (Windows, Linux, macOS)
- Lightweight (~500-700 lines expected)
- No heavy dependencies (unlike Flet)

#### 0.2. Dependencies
**To add to pyproject.toml:**
```toml
dependencies = [
    # ... existing ...
    "customtkinter>=5.2.0",  # UI framework
    "pillow>=10.0.0",        # Required by CustomTkinter
]

[optional-dependencies]
build = [
    "pyinstaller>=6.0.0",    # For creating exe
]
```

#### 0.3. Folder Structure
**To create:**
```
src/
└── ui_ctk/                    # New CustomTkinter folder
    ├── __init__.py
    ├── app.py                 # Main entry point
    ├── main_window.py         # Main window with navigation
    ├── views/                 # Application screens
    │   ├── __init__.py
    │   ├── employee_list.py   # Employee list
    │   ├── employee_detail.py # Employee detail
    │   ├── alerts_view.py     # Alerts view
    │   └── import_view.py     # Excel import
    ├── forms/                 # Input forms
    │   ├── __init__.py
    │   ├── employee_form.py   # Employee form
    │   ├── caces_form.py      # CACES form
    │   └── medical_form.py    # Medical visit form
    └── widgets/               # Reusable widgets
        ├── __init__.py
        ├── status_badge.py    # Colored status badge
        └── date_picker.py     # Date picker
```

**Deliverables:**
- ✅ Folder structure validated
- ✅ Dependencies identified
- ✅ Environment ready

---

## 🗄️ PHASE 1: DATA MODEL & MIGRATION

### Objectives
- Add contact fields to Employee model
- Create database migration
- Validate changes

### Tasks

#### 1.1. Update Employee Model
**Change in `src/employee/models.py`:**
```python
class Employee(Model):
    # ... existing ...

    # Contact Information (NEW)
    phone = CharField(null=True)      # Phone (optional)
    email = CharField(null=True)      # Email (optional)

    # ... rest existing ...
```

**Rationale:**
- Necessary to contact employees
- Explicitly requested for V1

#### 1.2. Create Migration Script
**File: `src/database/migrations/add_employee_contacts.py`**
```python
"""Migration: Add phone and email to Employee table."""

def upgrade():
    """Add phone and email columns to employees table."""
    db = database
    migrator = SqliteMigrator(db)

    # Add columns
    migrate(
        migrator.add_column('employees', 'phone', CharField(null=True)),
        migrator.add_column('employees', 'email', CharField(null=True)),
    )

def downgrade():
    """Remove phone and email columns."""
    db = database
    migrator = SqliteMigrator(db)

    migrate(
        migrator.drop_column('employees', 'phone'),
        migrator.drop_column('employees', 'email'),
    )
```

#### 1.3. Manual Migration Script
**File: `scripts/migrate_add_contacts.py`**
```python
"""Manual SQLite migration for contact fields."""

import sqlite3
from pathlib import Path

def migrate(db_path: str):
    """Add phone and email columns to employees table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add phone
        cursor.execute("ALTER TABLE employees ADD COLUMN phone TEXT")
        print("✅ Column 'phone' added")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠️ Column 'phone' already exists")
        else:
            raise

    try:
        # Add email
        cursor.execute("ALTER TABLE employees ADD COLUMN email TEXT")
        print("✅ Column 'email' added")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠️ Column 'email' already exists")
        else:
            raise

    conn.commit()
    conn.close()
    print("✅ Migration complete")
```

#### 1.4. Test Migration
1. Backup existing database
2. Run migration
3. Verify columns exist
4. Test creating employee with phone/email

**Deliverables:**
- ✅ Employee model updated with phone/email
- ✅ Working migration script
- ✅ Migration tested on database
- ✅ Migration documentation

---

## 🖼️ PHASE 2: CUSTOMTKINTER UI STRUCTURE

### Objectives
- Create basic application structure
- Implement main window with navigation
- Set up view switching system

### Tasks

#### 2.1. Entry Point (app.py)
**File: `src/ui_ctk/app.py`**

**Responsibilities:**
- Initialize CustomTkinter
- Create main window
- Initialize database connection
- Start main loop

**Pseudo-code:**
```python
import customtkinter as ctk
from database.connection import database
from ui_ctk.main_window import MainWindow

def main():
    """Application entry point."""
    # Setup CustomTkinter
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Create main window
    app = ctk.CTk()
    app.title("Wareflow EMS - Gestion des Salariés")
    app.geometry("1200x800")

    # Connect to database
    database.connect()
    database.create_tables([Employee, Caces, MedicalVisit, OnlineTraining])

    # Create main window with navigation
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Run
    app.mainloop()

    # Cleanup
    database.close()
```

#### 2.2. Main Window with Navigation (main_window.py)
**File: `src/ui_ctk/main_window.py`**

**Layout:**
```
┌────────────────────────────────────────────┐
│  Wareflow EMS - Gestion des Salariés       │
├────────────────────────────────────────────┤
│  [Employees] [Alerts] [Import]            │  ← Navigation Bar
├────────────────────────────────────────────┤
│                                            │
│                                            │
│            VIEW CONTENT                    │  ← View Container
│          (changes dynamically)             │
│                                            │
│                                            │
└────────────────────────────────────────────┘
```

**Responsibilities:**
- Create navigation bar
- Manage view switching
- Maintain global application state

**Pseudo-code:**
```python
import customtkinter as ctk
from ui_ctk.views.employee_list import EmployeeListView
from ui_ctk.views.alerts_view import AlertsView
from ui_ctk.views.import_view import ImportView

class MainWindow(ctk.CTkFrame):
    """Main window with navigation."""

    def __init__(self, master):
        super().__init__(master)

        # Navigation bar
        self.nav_bar = ctk.CTkFrame(self)
        self.nav_bar.pack(side="top", fill="x", padx=10, pady=10)

        # View container
        self.view_container = ctk.CTkFrame(self)
        self.view_container.pack(fill="both", expand=True)

        # Navigation buttons
        self.create_nav_buttons()

        # Show default view
        self.show_employee_list()

    def create_nav_buttons(self):
        """Create navigation buttons."""
        btn_employees = ctk.CTkButton(
            self.nav_bar,
            text="👥 Employés",
            command=self.show_employee_list
        )
        btn_employees.pack(side="left", padx=5)

        btn_alerts = ctk.CTkButton(
            self.nav_bar,
            text="⚠️ Alertes",
            command=self.show_alerts
        )
        btn_alerts.pack(side="left", padx=5)

        btn_import = ctk.CTkButton(
            self.nav_bar,
            text="📥 Import Excel",
            command=self.show_import
        )
        btn_import.pack(side="left", padx=5)

    def show_employee_list(self):
        """Show employee list view."""
        self.clear_view()
        EmployeeListView(self.view_container).pack(fill="both", expand=True)

    def show_alerts(self):
        """Show alerts view."""
        self.clear_view()
        AlertsView(self.view_container).pack(fill="both", expand=True)

    def show_import(self):
        """Show import view."""
        self.clear_view()
        ImportView(self.view_container).pack(fill="both", expand=True)

    def clear_view(self):
        """Remove current view."""
        for widget in self.view_container.winfo_children():
            widget.destroy()
```

**Deliverables:**
- ✅ Entry point created (app.py)
- ✅ Main window with navigation
- ✅ Working navigation buttons
- ✅ Operational view switching system

---

## 👥 PHASE 3: EMPLOYEE VIEWS

### Objectives
- Create employee list view
- Create employee detail view
- Create input forms

### Tasks

#### 3.1. Employee List View (employee_list.py)
**File: `src/ui_ctk/views/employee_list.py`**

**Layout:**
```
┌────────────────────────────────────────────┐
│  👥 Employee List                          │
├────────────────────────────────────────────┤
│  🔍 [Search........................]        │
│  📊 [Active ▼]                             │
├────────────────────────────────────────────┤
│  │ Name          │ Status  │ Actions    │  ← TableHeader
│  ├───────────────┼─────────┼────────────┤
│  │ Jean Dupont   │ Active  │ [Detail]   │  ← Row
│  │ Marie Martin  │ Active  │ [Detail]   │  ← Row
│  │ Pierre Bernard│ Inactive│ [Detail]   │  ← Row
│  └───────────────┴─────────┴────────────┘
│                    ↓                        ↓
│             [➕ Add]              [🔄 Refresh]│
└────────────────────────────────────────────┘
```

**Responsibilities:**
- Display employees in a table
- Allow search by name
- Filter by status (active/inactive)
- Button to view employee detail
- Button to add new employee

**Pseudo-code:**
```python
import customtkinter as ctk
from employee.models import Employee
from ui_ctk.forms.employee_form import EmployeeFormDialog
from ui_ctk.views.employee_detail import EmployeeDetailView

class EmployeeListView(ctk.CTkFrame):
    """Employee list view."""

    def __init__(self, master):
        super().__init__(master)

        # Header
        self.create_header()

        # Search and filter bar
        self.create_search_filter()

        # Employee table
        self.create_table()

        # Load employees
        self.refresh_employee_list()

    def create_header(self):
        """Create header."""
        header = ctk.CTkLabel(self, text="👥 Liste des Employés", font=("Arial", 20, "bold"))
        header.pack(pady=10)

    def create_search_filter(self):
        """Create search and filter bar."""
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search)
        search_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="🔍 Rechercher par nom...",
            textvariable=self.search_var
        )
        search_entry.pack(side="left", padx=5)

        # Filter
        self.filter_var = ctk.StringVar(value="all")
        filter_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["Tous", "Actifs", "Inactifs"],
            variable=self.filter_var,
            command=self.on_filter
        )
        filter_menu.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Rafraîchir",
            command=self.refresh_employee_list
        )
        refresh_btn.pack(side="right", padx=5)

    def create_table(self):
        """Create employee table."""
        # Scrollable frame
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header row
        self.create_table_header()

        # Data rows (placeholder)
        self.table_rows = []

    def create_table_header(self):
        """Create table header."""
        header_frame = ctk.CTkFrame(self.table_frame)
        header_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(header_frame, text="Nom", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Email", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Téléphone", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Statut", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Actions", font=("Arial", 12, "bold")).pack(side="right", padx=10)

    def refresh_employee_list(self):
        """Load employee list."""
        # Clear existing rows
        for row in self.table_rows:
            row.destroy()
        self.table_rows.clear()

        # Fetch employees
        employees = Employee.select()

        # Apply filter
        filter_value = self.filter_var.get()
        if filter_value == "Actifs":
            employees = employees.where(Employee.current_status == "active")
        elif filter_value == "Inactifs":
            employees = employees.where(Employee.current_status == "inactive")

        # Apply search
        search_term = self.search_var.get().lower()
        if search_term:
            employees = employees.where(
                (Employee.first_name.contains(search_term)) |
                (Employee.last_name.contains(search_term))
            )

        # Create rows
        for employee in employees:
            row = self.create_employee_row(employee)
            row.pack(fill="x", pady=2)
            self.table_rows.append(row)

    def create_employee_row(self, employee):
        """Create employee row."""
        row = ctk.CTkFrame(self.table_frame)

        name_label = ctk.CTkLabel(row, text=employee.full_name)
        name_label.pack(side="left", padx=10)

        email_label = ctk.CTkLabel(row, text=employee.email or "-")
        email_label.pack(side="left", padx=10)

        phone_label = ctk.CTkLabel(row, text=employee.phone or "-")
        phone_label.pack(side="left", padx=10)

        status_color = "green" if employee.is_active else "gray"
        status_label = ctk.CTkLabel(
            row,
            text="✓ Actif" if employee.is_active else "○ Inactif",
            text_color=status_color
        )
        status_label.pack(side="left", padx=10)

        detail_btn = ctk.CTkButton(
            row,
            text="Détail",
            width=80,
            command=lambda: self.show_employee_detail(employee)
        )
        detail_btn.pack(side="right", padx=5)

        return row

    def show_employee_detail(self, employee):
        """Show employee detail."""
        # Clear view and show detail
        self.master.clear_view()
        EmployeeDetailView(self.master.view_container, employee).pack(fill="both", expand=True)

    def on_search(self, *args):
        """Handle search."""
        self.refresh_employee_list()

    def on_filter(self, value):
        """Handle filter."""
        self.refresh_employee_list()

    def add_employee(self):
        """Add new employee."""
        dialog = EmployeeFormDialog(self)
        if dialog.result:
            self.refresh_employee_list()
```

#### 3.2. Employee Form (employee_form.py)
**File: `src/ui_ctk/forms/employee_form.py`**

**Responsibilities:**
- Employee create/edit form
- Field validation
- Save to database

**Form Layout:**
```
┌─────────────────────────────────────────┐
│  ➕ New Employee / ✏️ Edit              │
├─────────────────────────────────────────┤
│  First Name: [________________]  *      │
│  Last Name:  [________________]  *      │
│  Email:      [________________]         │
│  Phone:      [________]                 │
│  Status:     [Active ▼]      *          │
│  Workspace:  [________]       *          │
│  Role:       [________]       *          │
│  Contract:   [CDI ▼]         *          │
│  Entry Date: [DD/MM/YYYY]     *          │
│                                         │
│     [Cancel]              [Save]        │
└─────────────────────────────────────────┘
```

#### 3.3. Employee Detail View (employee_detail.py)
**File: `src/ui_ctk/views/employee_detail.py`**

**Layout:**
```
┌────────────────────────────────────────────┐
│  ← Back    Jean Dupont                    │
├────────────────────────────────────────────┤
│  Information                              │
│  ┌──────────────────────────────────────┐ │
│  │ Email: jean.dupont@example.com       │ │
│  │ Phone: 06 12 34 56 78                │ │
│  │ Status: Active                       │ │
│  │ Contract: CDI                        │ │
│  │ Workspace: Zone A                    │ │
│  │ Role: Forklift Operator              │ │
│  │ Entry Date: 15/01/2025               │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  CACES                    [➕ Add]       │
│  ┌──────────────────────────────────────┐ │
│  │ R489-1A | Expires: 15/01/2030 ✓     │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  Medical Visits          [➕ Add]        │
│  ┌──────────────────────────────────────┐ │
│  │ Periodic | Expires: 15/01/2027 ✓    │ │
│  └──────────────────────────────────────┘ │
│                                          │
│           [✏️ Edit] [🗑️ Delete]          │
└────────────────────────────────────────────┘
```

**Deliverables:**
- ✅ Working employee list view
- ✅ Operational search and filters
- ✅ Employee form with validation
- ✅ Complete employee detail view
- ✅ Full employee CRUD

---

## ⚠️ PHASE 4: ALERTS VIEW

### Objectives
- Create simple alerts view
- Implement type and day filters
- Display urgency-colored alerts

### Tasks

#### 4.1. Alerts View (alerts_view.py)
**File: `src/ui_ctk/views/alerts_view.py`**

**Layout:**
```
┌────────────────────────────────────────────┐
│  ⚠️ Alerts                                 │
├────────────────────────────────────────────┤
│  Type: [All ▼]    Days: [30 ▼]            │
├────────────────────────────────────────────┤
│  🔴 CACES R489-1A - Jean Dupont            │
│     Expires in 12 days (15/02/2025)        │
│     [View Detail]                          │
├────────────────────────────────────────────┤
│  🟡 Medical Visit - Marie Martin           │
│     Expires in 45 days (15/03/2025)        │
│     [View Detail]                          │
├────────────────────────────────────────────┤
│  🟢 CACES R489-3 - Pierre Bernard          │
│     Expires in 89 days (15/04/2025)        │
│     [View Detail]                          │
└────────────────────────────────────────────┘
```

**Available Filters:**
- **Type**: All, CACES, Medical Visits, Trainings
- **Days**: 30 (critical), 60 (warning), 90 (information), All

**Color Code:**
- 🔴 **Red**: Expired or less than 30 days
- 🟡 **Yellow**: 30-60 days
- 🟢 **Green**: 60-90 days
- ⚪ **Gray**: More than 90 days

**Deliverables:**
- ✅ Simple, clear alerts view
- ✅ Type and day filters
- ✅ Urgency-based coloring
- ✅ Link to employee detail

---

## 📥 PHASE 5: EXCEL IMPORT

### Objectives
- Create Excel import view
- Implement data validation
- Handle import errors

### Tasks

#### 5.1. Excel Import View (import_view.py)
**File: `src/ui_ctk/views/import_view.py`**

**Layout:**
```
┌────────────────────────────────────────────┐
│  📥 Excel Import                           │
├────────────────────────────────────────────┤
│  Import an Excel file containing           │
│  the list of employees to import.          │
│                                          │
│  [Choose Excel File...]                    │
│                                          │
│  Expected format:                          │
│  ┌──────────────────────────────────────┐ │
│  │ First | Last | Email | Phone |      │ │
│  │ Name  | Name  |      |       |      │ │
│  │ Jean  | Dupont | ... | ...        │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  [📥 Download Template]                   │
│                                          │
│  ┌──────────────────────────────────────┐ │
│  │ Progress: ████░░░░░░ 50%            │ │
│  │ 5 employees imported / 10            │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  [Import]                                 │
└────────────────────────────────────────────┘
```

**Features:**
- Excel file selection
- Format validation
- Progress display
- Error reporting (line by line)
- Cancellation support

**Deliverables:**
- ✅ Working Excel import view
- ✅ Data validation
- ✅ Error handling
- ✅ Detailed import report

---

## 🧪 PHASE 6: TESTING & VALIDATION

### Objectives
- Test all features
- Fix bugs
- Validate UX

### Tasks

#### 6.1. Manual Testing

**Test Scenarios:**

1. **Employee CRUD:**
   - ✅ Create employee with all fields
   - ✅ Create employee with only required fields
   - ✅ Edit existing employee
   - ✅ Delete employee (with confirmation)
   - ✅ Search employee by name
   - ✅ Filter by status (active/inactive)

2. **CACES & Visits:**
   - ✅ Add CACES (verify expiration calculation)
   - ✅ Add medical visit (verify calculation)
   - ✅ Check status (valid, warning, critical, expired)

3. **Alerts:**
   - ✅ Display CACES alerts
   - ✅ Display medical visit alerts
   - ✅ Filter by type
   - ✅ Filter by days (30, 60, 90)
   - ✅ Verify coloring

4. **Excel Import:**
   - ✅ Import valid file
   - ✅ Import file with errors (verify handling)
   - ✅ Import file with incorrect formats
   - ✅ Cancel import in progress

5. **Navigation:**
   - ✅ Change views without errors
   - ✅ Return to list from detail
   - ✅ Data persistence between views

#### 6.2. Performance Testing

- ✅ List load time (with 100+ employees)
- ✅ Search speed
- ✅ Navigation fluidity
- ✅ Memory usage

#### 6.3. UX Testing

- ✅ Interface intuitiveness
- ✅ Error message clarity
- ✅ Accessibility (button size, readability)
- ✅ Visual consistency

**Deliverables:**
- ✅ All scenarios tested
- ✅ Bugs fixed
- ✅ UX validated

---

## 📦 PHASE 7: BUILD & DEPLOYMENT

### Objectives
- Create .exe executable
- Test executable
- Prepare deployment

### Tasks

#### 7.1. PyInstaller Configuration

**File: `build.spec`**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/ui_ctk/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/database', 'src/database'),
        ('src/employee', 'src/employee'),
        ('src/controllers', 'src/controllers'),
        ('src/state', 'src/state'),
        ('src/lock', 'src/lock'),
    ],
    hiddenimports=[
        'peewee',
        'customtkinter',
        'PIL',
        'dateutil',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WareflowEMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No Windows console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # Optional
)
```

#### 7.2. Build Script

**File: `scripts/build.bat`**
```batch
@echo off
echo ========================================
echo Build Wareflow EMS
echo ========================================

echo.
echo [1/4] Cleaning...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [2/4] Installing dependencies...
pip install -e .

echo.
echo [3/4] PyInstaller build...
pyinstaller build.spec --clean

echo.
echo [4/4] Done!
echo.
echo Executable is in: dist\WareflowEMS.exe
pause
```

#### 7.3. Deployment Structure

**Folder to deploy:**
```
[Gestion_Salaries_2025/
├── WareflowEMS.exe              # Application
├── data/                        # Data (created on first run)
│   └── employee_manager.db      # SQLite database
├── documents/                   # Uploaded documents
│   ├── caces/                   # CACES certificates
│   ├── medical/                 # Medical visits
│   └── training/                # Trainings
└── README.txt                   # Instructions
```

#### 7.4. Executable Testing

- ✅ Launch without errors
- ✅ Database connection
- ✅ All features tested
- ✅ Acceptable performance
- ✅ No missing dependencies

**Deliverables:**
- ✅ Working .exe executable
- ✅ Ready deployment structure
- ✅ Installation instructions
- ✅ User README

---

## 📊 PLAN SUMMARY

### Estimated Duration per Phase

| Phase | Duration | Complexity |
|-------|----------|------------|
| **Phase 0** | Preparation | 2h | Low |
| **Phase 1** | Model & Migration | 2h | Low |
| **Phase 2** | UI Structure | 4h | Medium |
| **Phase 3** | Employee Views | 8h | Medium |
| **Phase 4** | Alerts View | 4h | Low |
| **Phase 5** | Excel Import | 6h | Medium |
| **Phase 6** | Testing | 4h | Low |
| **Phase 7** | Build | 2h | Low |
| **TOTAL** | **32h** (~5-7 days) | - |

### Phase Dependencies

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 6 → Phase 7
                              ↘
                               Phase 4 ↗
                               Phase 5 ↗
```

### Control Points

- **End Phase 1**: Migration validated ✅
- **End Phase 3**: Working employee CRUD ✅
- **End Phase 5**: All views implemented ✅
- **End Phase 6**: Application tested and validated ✅
- **End Phase 7**: Deployment-ready .exe ✅

---

## 🎯 SUCCESS CRITERIA

### Functional
- ✅ Complete employee CRUD
- ✅ Add CACES and medical visits
- ✅ Working alerts view
- ✅ Working Excel import
- ✅ Persistent SQLite database

### Non-Functional
- ✅ French language UI
- ✅ Modern design (CustomTkinter)
- ✅ Acceptable performance (<2s to load 100 employees)
- ✅ Standalone .exe executable
- ✅ Single connection (lock manager)

### UX
- ✅ Intuitive interface
- ✅ Clear error messages
- ✅ Fluid navigation
- ✅ User feedback (progress, confirmations)

---

## 🚀 NEXT STEPS

**Immediate:**
1. Get user validation for this plan
2. Add CustomTkinter dependencies to project
3. Start Phase 0 (Preparation)

**After validation:**
- Follow phases sequentially
- Mark each phase as complete
- Frequent commits
- Test after each phase

**Happy development! 🎉**
