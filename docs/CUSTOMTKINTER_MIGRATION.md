# CustomTkinter Migration Plan

## Overview

This document outlines the complete development plan for migrating the Warehouse Employee Management System (Wareflow EMS) from Flet to CustomTkinter.

**Status:** Flet UI layer removed ✅ | CustomTkinter implementation pending

**Objective:** Create a simple, maintainable, disposable desktop UI (~700-1000 lines of code)

**Philosophy:** Progressive development with atomic commits and continuous testing

---

## Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Development Phases](#development-phases)
4. [Implementation Details](#implementation-details)
5. [Testing Strategy](#testing-strategy)
6. [Timeline & Milestones](#timeline--milestones)
7. [Technical Decisions](#technical-decisions)

---

## Architecture

### Current State (Post-Flet Removal)

```
src/
├── controllers/          # ✅ Business logic (reusable)
│   ├── dashboard_controller.py
│   ├── employee_controller.py
│   └── alerts_controller.py
├── state/               # ✅ Global state (reusable)
│   └── app_state.py
├── database/            # ✅ Database layer (preserved)
├── employee/            # ✅ Employee models & queries (preserved)
├── lock/                # ✅ Lock manager (preserved)
└── cli/                 # ✅ CLI interface (preserved)
```

### Target Architecture

```
src/
├── ui_ctk/              # 🆕 CustomTkinter UI (new)
│   ├── app.py          # Main application entry point
│   ├── views.py        # All view implementations
│   ├── dialogs.py      # Form dialogs
│   └── constants.py    # UI constants
├── controllers/         # ✅ Existing (reused)
├── state/              # ✅ Existing (reused)
└── ...                 # ✅ Other modules (unchanged)
```

### Key Design Principles

1. **Simplicity:** Maximum 3-4 files for the entire UI
2. **Reuse:** Leverage existing controllers and models
3. **No Abstraction:** Direct CustomTkinter usage, no wrapper classes
4. **Progressive:** Build one feature at a time, test, commit
5. **Disposable:** Code is easy to replace, not over-engineered

---

## Project Structure

### New Files to Create

```
src/ui_ctk/
├── __init__.py           # Package initialization
├── app.py               # Main application class (~150 lines)
│   ├── WarehouseEMS (ctk.CTk)
│   ├── Window setup
│   ├── Sidebar navigation
│   ├── View switching logic
│   └── Lock management
│
├── views.py             # All view implementations (~400 lines)
│   ├── build_dashboard()          # Dashboard view
│   ├── build_employee_list()      # Employee list view
│   ├── build_employee_detail()    # Employee detail view
│   └── build_alerts()             # Alerts view
│
├── dialogs.py           # Form dialogs (~200 lines)
│   ├── EmployeeFormDialog          # Employee create/edit
│   ├── CacesFormDialog             # CACES certification
│   ├── MedicalVisitFormDialog      # Medical visit
│   ├── TrainingFormDialog          # Online training
│   └── ConfirmDialog               # Generic confirmation
│
└── constants.py         # UI constants (~50 lines)
    ├── Color constants
    ├── Status colors
    ├── Spacing constants
    └── Font sizes
```

### Dependencies to Add

**File:** `pyproject.toml`

```toml
dependencies = [
    "peewee>=3.17.0",
    "python-dateutil>=2.8.0",
    "customtkinter>=5.2.0",     # 🆕 Add this
    "openpyxl>=3.1.0",
    "typer[all]>=0.12.0",
    "rich>=13.7.0",
    "tabulate>=0.9.0",
    "questionary>=2.0.0",
]
```

---

## Development Phases

### Phase 1: Foundation Setup (1-2 days)

**Goal:** Basic app shell with navigation

#### Step 1.1: Project Structure & Dependencies

**Tasks:**
- [ ] Create `src/ui_ctk/` directory
- [ ] Add `customtkinter>=5.2.0` to `pyproject.toml`
- [ ] Run `uv sync`
- [ ] Create `__init__.py`

**Commit Message:**
```
feat: setup CustomTkinter project structure

- Add customtkinter>=5.2.0 dependency
- Create src/ui_ctk/ directory with __init__.py
```

---

#### Step 1.2: Main Application Shell

**File:** `src/ui_ctk/app.py`

**Implementation:**
```python
"""CustomTkinter application entry point."""

import customtkinter as ctk
from pathlib import Path
from state import get_app_state
from controllers.dashboard_controller import DashboardController
from controllers.employee_controller import EmployeeController
from controllers.alerts_controller import AlertsController
from database.connection import database


class WarehouseEMS(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Wareflow EMS")
        self.geometry("1200x700")

        # Initialize database
        self._init_database()

        # Initialize state
        self.state = get_app_state()
        if not self.state.acquire_lock():
            self._show_lock_error()
            return

        # Controllers
        self.controllers = {
            'dashboard': DashboardController(),
            'employee': EmployeeController(),
            'alerts': AlertsController(),
        }

        # Create UI
        self._create_sidebar()
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Show default view
        self.show_dashboard()

        # Handle close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_database(self):
        """Initialize database connection."""
        db_path = Path("employee_manager.db")
        if not db_path.exists():
            from database.connection import init_database
            init_database(db_path)
        database.init(db_path)

    def _create_sidebar(self):
        """Create navigation sidebar."""
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo/Title
        ctk.CTkLabel(
            sidebar,
            text="Wareflow",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=30)

        # Navigation buttons
        ctk.CTkButton(
            sidebar,
            text="📊 Dashboard",
            command=self.show_dashboard,
            height=40
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            sidebar,
            text="👥 Employees",
            command=self.show_employees,
            height=40
        ).pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            sidebar,
            text="⚠️ Alerts",
            command=self.show_alerts,
            height=40
        ).pack(pady=5, padx=10, fill="x")

    def show_dashboard(self):
        """Display dashboard view."""
        from ui_ctk.views import build_dashboard
        self._switch_view(build_dashboard(self, self.controllers['dashboard']))

    def show_employees(self):
        """Display employee list view."""
        from ui_ctk.views import build_employee_list
        self._switch_view(build_employee_list(self, self.controllers['employee']))

    def show_alerts(self):
        """Display alerts view."""
        from ui_ctk.views import build_alerts
        self._switch_view(build_alerts(self, self.controllers['alerts']))

    def _switch_view(self, view_frame):
        """Replace current view with new view."""
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
        self.current_view = view_frame
        self.current_view.pack(fill="both", expand=True)

    def _on_close(self):
        """Handle window close event."""
        self.state.release_lock()
        self.destroy()

    def _show_lock_error(self):
        """Show lock acquisition error."""
        ctk.CTkLabel(
            self,
            text=f"Lock Error: {self.state.lock_status}",
            text_color="red"
        ).pack(expand=True)


def main():
    """Application entry point."""
    app = WarehouseEMS()
    app.mainloop()


if __name__ == "__main__":
    main()
```

**Commit Message:**
```
feat: implement main application shell with navigation

- Create WarehouseEMS main application class
- Implement sidebar navigation with emoji icons
- Add database initialization
- Integrate lock manager
- Implement view switching mechanism
- Handle window close event
```

---

### Phase 2: Core Views (3-5 days)

**Goal:** Implement all main views with data display

#### Step 2.1: Dashboard View

**File:** `src/ui_ctk/views.py` - `build_dashboard()`

**Features:**
- Statistics cards (4 cards)
  - Total employees
  - Active employees
  - Expiring certifications (30 days)
  - Unfit employees
- Compliance percentage indicator
- Recent alerts list

**Implementation:**
```python
def build_dashboard(app, controller):
    """Build dashboard view."""
    frame = ctk.CTkFrame(app.main_container)

    # Header
    header = ctk.CTkLabel(
        frame,
        text="Dashboard",
        font=ctk.CTkFont(size=28, weight="bold")
    )
    header.pack(pady=20)

    # Statistics
    stats = controller.get_statistics()

    stats_frame = ctk.CTkFrame(frame)
    stats_frame.pack(fill="x", padx=20, pady=10)

    # Create stat cards
    _create_stat_card(stats_frame, "Total Employees", stats['total_employees'], "👥", 0)
    _create_stat_card(stats_frame, "Active", stats['active_employees'], "✅", 1)
    _create_stat_card(stats_frame, "Expiring", stats['expiring_caces'], "⚠️", 2)
    _create_stat_card(stats_frame, "Unfit", stats['unfit_employees'], "❌", 3)

    # Compliance percentage
    compliance = controller.get_compliance_percentage()
    compliance_frame = ctk.CTkFrame(frame)
    compliance_frame.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(
        compliance_frame,
        text=f"Global Compliance: {compliance}%",
        font=ctk.CTkFont(size=18)
    ).pack(pady=10)

    # Recent alerts
    alerts = controller.get_alerts(days=30)
    alerts_frame = ctk.CTkFrame(frame)
    alerts_frame.pack(fill="both", expand=True, padx=20, pady=10)

    ctk.CTkLabel(
        alerts_frame,
        text=f"Recent Alerts ({len(alerts)} employees)",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=10)

    # Scrollable alerts list
    alert_list = ctk.CTkScrollableFrame(alerts_frame, height=300)
    alert_list.pack(fill="both", expand=True, padx=10, pady=10)

    for emp_id, data in list(alerts.items())[:10]:  # Show first 10
        _create_alert_item(alert_list, data)

    return frame


def _create_stat_card(parent, title, value, icon, column):
    """Create a statistics card."""
    card = ctk.CTkFrame(parent)
    card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")

    ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=32)).pack(pady=10)
    ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=24, weight="bold")).pack()
    ctk.CTkLabel(card, text=title).pack(pady=5)

    parent.grid_columnconfigure(column, weight=1)


def _create_alert_item(parent, data):
    """Create an alert list item."""
    emp = data['employee']
    item = ctk.CTkFrame(parent)

    ctk.CTkLabel(
        item,
        text=emp.full_name,
        font=ctk.CTkFont(weight="bold")
    ).pack(anchor="w", padx=10, pady=5)

    # Alert badges
    alerts_count = (
        len(data['caces']) +
        len(data['medical_visits']) +
        len(data['trainings'])
    )

    ctk.CTkLabel(
        item,
        text=f"{alerts_count} expiring items",
        text_color="orange"
    ).pack(anchor="w", padx=10, pady=5)

    item.pack(fill="x", pady=5)
```

**Data Sources:**
- `DashboardController.get_statistics()` → Returns dict with counts
- `DashboardController.get_compliance_percentage()` → Returns int (0-100)
- `DashboardController.get_alerts(days=30)` → Returns dict grouped by employee

**Testing Checklist:**
- [ ] Statistics display correct numbers
- [ ] Compliance percentage shows
- [ ] Alerts list displays
- [ ] Scrollable area works
- [ ] No crashes with empty database

**Commit Message:**
```
feat: implement dashboard view with statistics and alerts

- Add 4 statistics cards (total, active, expiring, unfit)
- Display global compliance percentage
- Show recent alerts list (scrollable)
- Integrate with DashboardController
```

---

#### Step 2.2: Employee List View

**File:** `src/ui_ctk/views.py` - `build_employee_list()`

**Features:**
- Search bar (text search)
- Filter dropdown (all/active/inactive)
- Employee table (ttk.Treeview)
  - Columns: Name, Role, Workspace, Status, Compliance Score
  - Color-coded status
  - Click to view detail
- Action buttons (Add, Refresh)

**Implementation:**
```python
def build_employee_list(app, controller):
    """Build employee list view."""
    frame = ctk.CTkFrame(app.main_container)

    # Header
    header = ctk.CTkLabel(
        frame,
        text="Employees",
        font=ctk.CTkFont(size=28, weight="bold")
    )
    header.pack(pady=20)

    # Search and filter bar
    controls_frame = ctk.CTkFrame(frame)
    controls_frame.pack(fill="x", padx=20, pady=10)

    # Search entry
    search_entry = ctk.CTkEntry(controls_frame, placeholder_text="Search employees...")
    search_entry.pack(side="left", padx=10, expand=True, fill="x")

    # Filter dropdown
    filter_var = ctk.StringVar(value="all")
    filter_menu = ctk.CTkOptionMenu(
        controls_frame,
        values=["all", "active", "inactive"],
        variable=filter_var,
        command=lambda v: _refresh_employee_list(tree, controller, search_entry.get(), v)
    )
    filter_menu.pack(side="left", padx=10)

    # Refresh button
    refresh_btn = ctk.CTkButton(
        controls_frame,
        text="Refresh",
        command=lambda: _refresh_employee_list(tree, controller, search_entry.get(), filter_var.get())
    )
    refresh_btn.pack(side="left", padx=10)

    # Add employee button
    add_btn = ctk.CTkButton(
        controls_frame,
        text="Add Employee",
        fg_color="green",
        command=lambda: _open_employee_form(app, controller, tree)
    )
    add_btn.pack(side="left", padx=10)

    # Employee table
    import tkinter as tk
    from tkinter import ttk

    table_frame = ctk.CTkFrame(frame)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("name", "role", "workspace", "status", "score")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

    tree.heading("name", text="Name")
    tree.heading("role", text="Role")
    tree.heading("workspace", text="Workspace")
    tree.heading("status", text="Status")
    tree.heading("score", text="Score")

    tree.column("name", width=250)
    tree.column("role", width=150)
    tree.column("workspace", width=150)
    tree.column("status", width=100)
    tree.column("score", width=80)

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bind double-click to view detail
    tree.bind("<Double-1>", lambda e: _on_employee_select(app, tree, controller))

    # Load data
    _refresh_employee_list(tree, controller, "", "all")

    return frame


def _refresh_employee_list(tree, controller, search_text, status_filter):
    """Refresh employee list with filters."""
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)

    # Get employees
    employees = controller.get_all_employees()

    # Apply filters
    for emp in employees:
        # Status filter
        if status_filter == "active" and emp.current_status != "active":
            continue
        if status_filter == "inactive" and emp.current_status == "active":
            continue

        # Search filter
        if search_text and search_text.lower() not in emp.full_name.lower():
            continue

        # Get compliance score
        from employee import calculations
        score_data = calculations.calculate_compliance_score(emp)

        # Insert row
        tree.insert("", "end", iid=emp.id, values=(
            emp.full_name,
            emp.role or "N/A",
            emp.workspace or "N/A",
            emp.current_status,
            f"{score_data['score']}%"
        ))


def _on_employee_select(app, tree, controller):
    """Handle employee row double-click."""
    selection = tree.selection()
    if selection:
        emp_id = selection[0]
        app.show_employee_detail(emp_id)


def _open_employee_form(app, controller, tree):
    """Open employee form dialog."""
    from ui_ctk.dialogs import EmployeeFormDialog

    dialog = EmployeeFormDialog(app, controller)
    app.wait_window(dialog)

    # Refresh list after dialog closes
    _refresh_employee_list(tree, controller, "", "all")
```

**Testing Checklist:**
- [ ] Search filters by name
- [ ] Status filter works
- [ ] Double-click opens detail
- [ ] Add button opens form
- [ ] Refresh button reloads data
- [ ] Color coding for status (green=active, red=unfit)

**Commit Message:**
```
feat: implement employee list view with search and filters

- Add employee table with Treeview
- Implement text search functionality
- Add status filter dropdown (all/active/inactive)
- Double-click to view employee detail
- Add employee button opens form
- Refresh button reloads data
```

---

#### Step 2.3: Employee Detail View

**File:** `src/ui_ctk/views.py` - `build_employee_detail()`

**Features:**
- Employee info card
  - Photo placeholder
  - Name, role, workspace
  - Status badge
  - Large compliance score
- Certifications sections
  - CACES list (type, number, issue date, expiration)
  - Medical visits (date, result, next visit)
  - Online trainings (name, completion, expiration)
- Action buttons (Edit, Add Certification, Back)

**Implementation:**
```python
def build_employee_detail(app, controller, employee_id):
    """Build employee detail view."""
    frame = ctk.CTkFrame(app.main_container)

    # Get employee data
    details = controller.get_employee_details(str(employee_id))
    if not details:
        ctk.CTkLabel(frame, text="Employee not found").pack(expand=True)
        return frame

    emp = details['employee']
    score = details['compliance_score']
    caces = details['caces_list']
    visits = details['medical_visits']
    trainings = details['trainings']

    # Header with back button
    header_frame = ctk.CTkFrame(frame)
    header_frame.pack(fill="x", padx=20, pady=10)

    ctk.CTkButton(
        header_frame,
        text="← Back",
        command=app.show_employees
    ).pack(side="left", padx=10)

    ctk.CTkLabel(
        header_frame,
        text="Employee Details",
        font=ctk.CTkFont(size=24, weight="bold")
    ).pack(side="left", padx=20)

    # Employee info card
    info_frame = ctk.CTkFrame(frame)
    info_frame.pack(fill="x", padx=20, pady=10)

    # Left: photo placeholder
    photo_frame = ctk.CTkFrame(info_frame, width=150, height=150)
    photo_frame.pack(side="left", padx=20, pady=20)
    ctk.CTkLabel(photo_frame, text="📷", font=ctk.CTkFont(size=48)).pack(expand=True)

    # Right: info
    details_frame = ctk.CTkFrame(info_frame)
    details_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        details_frame,
        text=emp.full_name,
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(anchor="w", pady=5)

    ctk.CTkLabel(details_frame, text=f"Role: {emp.role or 'N/A'}").pack(anchor="w", pady=2)
    ctk.CTkLabel(details_frame, text=f"Workspace: {emp.workspace or 'N/A'}").pack(anchor="w", pady=2)
    ctk.CTkLabel(details_frame, text=f"Status: {emp.current_status}").pack(anchor="w", pady=2)

    # Compliance score
    score_color = _get_score_color(score)
    ctk.CTkLabel(
        details_frame,
        text=f"Compliance: {score}%",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=score_color
    ).pack(anchor="w", pady=10)

    # Certifications section
    _create_certifications_section(frame, caces, visits, trainings)

    # Action buttons
    actions_frame = ctk.CTkFrame(frame)
    actions_frame.pack(fill="x", padx=20, pady=10)

    ctk.CTkButton(
        actions_frame,
        text="Edit Employee",
        command=lambda: _open_edit_employee_dialog(app, controller, emp_id)
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        actions_frame,
        text="Add CACES",
        command=lambda: _open_caces_dialog(app, emp_id)
    ).pack(side="left", padx=10)

    return frame


def _create_certifications_section(parent, caces, visits, trainings):
    """Create certifications display section."""
    tabs_frame = ctk.CTkFrame(parent)
    tabs_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Tab buttons
    tab_frame = ctk.CTkFrame(tabs_frame)
    tab_frame.pack(fill="x", padx=10, pady=10)

    # Content frame
    content_frame = ctk.CTkScrollableFrame(tabs_frame, height=300)
    content_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Display CACES
    for cert in caces:
        _create_cert_item(content_frame, cert)

    # Display medical visits
    for visit in visits:
        _create_visit_item(content_frame, visit)

    # Display trainings
    for training in trainings:
        _create_training_item(content_frame, training)


def _create_cert_item(parent, cert):
    """Create certification item."""
    item = ctk.CTkFrame(parent)

    status_color = "red" if cert.is_expired else "green"
    status_text = "Expired" if cert.is_expired else "Valid"

    ctk.CTkLabel(item, text=f"CACES - {cert.certificate_type}").pack(anchor="w", padx=10, pady=5)
    ctk.CTkLabel(item, text=f"Number: {cert.certificate_number}").pack(anchor="w", padx=10)
    ctk.CTkLabel(item, text=f"Expires: {cert.expiration_date}").pack(anchor="w", padx=10)
    ctk.CTkLabel(item, text=f"Status: {status_text}", text_color=status_color).pack(anchor="w", padx=10, pady=5)

    item.pack(fill="x", pady=5)


def _create_visit_item(parent, visit):
    """Create medical visit item."""
    item = ctk.CTkFrame(parent)

    status_color = "red" if visit.is_expired else "green"
    status_text = "Expired" if visit.is_expired else visit.result

    ctk.CTkLabel(item, text="Medical Visit").pack(anchor="w", padx=10, pady=5)
    ctk.CTkLabel(item, text=f"Date: {visit.visit_date}").pack(anchor="w", padx=10)
    ctk.CTkLabel(item, text=f"Result: {status_text}", text_color=status_color).pack(anchor="w", padx=10, pady=5)

    item.pack(fill="x", pady=5)


def _create_training_item(parent, training):
    """Create training item."""
    item = ctk.CTkFrame(parent)

    status_color = "red" if training.is_expired else "green"
    status_text = "Expired" if training.is_expired else "Valid"

    ctk.CTkLabel(item, text=f"Training: {training.training_name}").pack(anchor="w", padx=10, pady=5)
    ctk.CTkLabel(item, text=f"Completed: {training.completion_date}").pack(anchor="w", padx=10)
    ctk.CTkLabel(item, text=f"Expires: {training.expiration_date}").pack(anchor="w", padx=10)
    ctk.CTkLabel(item, text=f"Status: {status_text}", text_color=status_color).pack(anchor="w", padx=10, pady=5)

    item.pack(fill="x", pady=5)


def _get_score_color(score):
    """Get color based on compliance score."""
    if score >= 70:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"
```

**Testing Checklist:**
- [ ] Employee info displays correctly
- [ ] Compliance score shows with color
- [ ] Certifications display in sections
- [ ] Status indicators show (valid/expired)
- [ ] Back button returns to list
- [ ] Edit button opens form

**Commit Message:**
```
feat: implement employee detail view with certifications

- Display employee information card
- Show compliance score with color coding
- List CACES certifications with status
- List medical visits with results
- List online trainings
- Add action buttons (edit, add certification)
- Implement back navigation
```

---

#### Step 2.4: Alerts View

**File:** `src/ui_ctk/views.py` - `build_alerts()`

**Features:**
- Filter controls (days threshold, alert type)
- Alerts list grouped by employee
- Export button (CSV)

**Implementation:**
```python
def build_alerts(app, controller):
    """Build alerts view."""
    frame = ctk.CTkFrame(app.main_container)

    # Header
    header = ctk.CTkLabel(
        frame,
        text="Alerts",
        font=ctk.CTkFont(size=28, weight="bold")
    )
    header.pack(pady=20)

    # Filter controls
    controls_frame = ctk.CTkFrame(frame)
    controls_frame.pack(fill="x", padx=20, pady=10)

    # Days threshold
    ctk.CTkLabel(controls_frame, text="Days:").pack(side="left", padx=10)
    days_var = ctk.StringVar(value="30")
    days_menu = ctk.CTkOptionMenu(
        controls_frame,
        values=["30", "60", "90"],
        variable=days_var
    )
    days_menu.pack(side="left", padx=10)

    # Export button
    export_btn = ctk.CTkButton(
        controls_frame,
        text="Export CSV",
        command=lambda: _export_alerts(controller, int(days_var.get()))
    )
    export_btn.pack(side="right", padx=10)

    # Alerts list
    alerts_frame = ctk.CTkScrollableFrame(frame, height=500)
    alerts_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Load alerts
    _refresh_alerts(alerts_frame, controller, 30)

    return frame


def _refresh_alerts(parent, controller, days):
    """Refresh alerts list."""
    # Clear existing
    for widget in parent.winfo_children():
        widget.destroy()

    # Get alerts
    alerts = controller.get_alerts(days=days)

    # Display grouped by employee
    for emp_id, data in alerts.items():
        _create_alert_group(parent, data)


def _create_alert_group(parent, data):
    """Create alert group for employee."""
    emp = data['employee']

    group = ctk.CTkFrame(parent)
    group.pack(fill="x", pady=10, padx=10)

    # Employee name
    ctk.CTkLabel(
        group,
        text=emp.full_name,
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(anchor="w", padx=10, pady=5)

    # CACES alerts
    for cert in data['caces']:
        item = ctk.CTkFrame(group)
        item.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(item, text=f"⚠️ CACES {cert.certificate_type} expires {cert.expiration_date}").pack(anchor="w", padx=5)

    # Medical visit alerts
    for visit in data['medical_visits']:
        item = ctk.CTkFrame(group)
        item.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(item, text=f"⚠️ Medical visit expires {visit.expiration_date}").pack(anchor="w", padx=5)

    # Training alerts
    for training in data['trainings']:
        item = ctk.CTkFrame(group)
        item.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(item, text=f"⚠️ Training {training.training_name} expires {training.expiration_date}").pack(anchor="w", padx=5)


def _export_alerts(controller, days):
    """Export alerts to CSV."""
    import csv
    from datetime import datetime

    alerts = controller.get_alerts(days=days)

    filename = f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Employee', 'Type', 'Description', 'Expiration'])

        for emp_id, data in alerts.items():
            emp = data['employee']

            for cert in data['caces']:
                writer.writerow([
                    emp.full_name,
                    'CACES',
                    cert.certificate_type,
                    cert.expiration_date
                ])

            for visit in data['medical_visits']:
                writer.writerow([
                    emp.full_name,
                    'Medical',
                    visit.result,
                    visit.expiration_date
                ])

            for training in data['trainings']:
                writer.writerow([
                    emp.full_name,
                    'Training',
                    training.training_name,
                    training.expiration_date
                ])

    print(f"Exported to {filename}")
```

**Testing Checklist:**
- [ ] Days filter updates alerts
- [ ] All alert types display
- [ ] Export CSV works
- [ ] Grouping by employee works

**Commit Message:**
```
feat: implement alerts view with filtering and export

- Add alerts list grouped by employee
- Implement days threshold filter (30/60/90)
- Display all alert types (CACES, medical, training)
- Add CSV export functionality
- Integrate with AlertsController
```

---

### Phase 3: Forms & Dialogs (2-3 days)

**Goal:** Implement all data entry forms

#### Step 3.1: Employee Form Dialog

**File:** `src/ui_ctk/dialogs.py` - `EmployeeFormDialog`

**Features:**
- Modal dialog
- Form fields with validation
- Save/Cancel buttons
- Create or update mode

**Implementation:**
```python
"""Form dialogs for data entry."""

import customtkinter as ctk
from datetime import datetime


class EmployeeFormDialog(ctk.CTkToplevel):
    """Dialog for creating/editing employees."""

    def __init__(self, parent, controller, employee_id=None):
        super().__init__(parent)

        self.controller = controller
        self.employee_id = employee_id
        self.result = None

        self.title("Employee Form")
        self.geometry("500x600")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build form
        self._build_form()

        # Load employee data if editing
        if employee_id:
            self._load_employee()

    def _build_form(self):
        """Build form fields."""
        form_frame = ctk.CTkScrollableFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # First name
        ctk.CTkLabel(form_frame, text="First Name *").pack(anchor="w", pady=(10, 0))
        self.first_name_entry = ctk.CTkEntry(form_frame)
        self.first_name_entry.pack(fill="x", pady=5)

        # Last name
        ctk.CTkLabel(form_frame, text="Last Name *").pack(anchor="w", pady=(10, 0))
        self.last_name_entry = ctk.CTkEntry(form_frame)
        self.last_name_entry.pack(fill="x", pady=5)

        # Role
        ctk.CTkLabel(form_frame, text="Role").pack(anchor="w", pady=(10, 0))
        self.role_combo = ctk.CTkComboBox(
            form_frame,
            values=["Operator", "Forklift Driver", "Warehouse Manager", "Supervisor", ""]
        )
        self.role_combo.pack(fill="x", pady=5)
        self.role_combo.set("")

        # Workspace
        ctk.CTkLabel(form_frame, text="Workspace").pack(anchor="w", pady=(10, 0))
        self.workspace_entry = ctk.CTkEntry(form_frame)
        self.workspace_entry.pack(fill="x", pady=5)

        # Status
        ctk.CTkLabel(form_frame, text="Status *").pack(anchor="w", pady=(10, 0))
        self.status_combo = ctk.CTkComboBox(
            form_frame,
            values=["active", "inactive", "medical_leave", "unfit"]
        )
        self.status_combo.pack(fill="x", pady=5)
        self.status_combo.set("active")

        # Hire date
        ctk.CTkLabel(form_frame, text="Hire Date").pack(anchor="w", pady=(10, 0))
        self.hire_date_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
        self.hire_date_entry.pack(fill="x", pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            fg_color="gray"
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._on_save,
            fg_color="green"
        ).pack(side="right", padx=10)

    def _load_employee(self):
        """Load employee data for editing."""
        emp = self.controller.get_employee_by_id(str(self.employee_id))
        if emp:
            self.first_name_entry.insert(0, emp.first_name or "")
            self.last_name_entry.insert(0, emp.last_name or "")
            self.role_combo.set(emp.role or "")
            self.workspace_entry.insert(0, emp.workspace or "")
            self.status_combo.set(emp.current_status)
            if emp.hire_date:
                self.hire_date_entry.insert(0, str(emp.hire_date))

    def _validate(self):
        """Validate form fields."""
        if not self.first_name_entry.get().strip():
            return False, "First name is required"

        if not self.last_name_entry.get().strip():
            return False, "Last name is required"

        # Validate date format
        hire_date = self.hire_date_entry.get().strip()
        if hire_date:
            try:
                datetime.strptime(hire_date, "%Y-%m-%d")
            except ValueError:
                return False, "Invalid date format (use YYYY-MM-DD)"

        return True, None

    def _on_save(self):
        """Handle save button."""
        is_valid, error = self._validate()
        if not is_valid:
            ctk.CTkLabel(self, text=error, text_color="red").pack()
            return

        # Collect data
        data = {
            'first_name': self.first_name_entry.get().strip(),
            'last_name': self.last_name_entry.get().strip(),
            'role': self.role_combo.get(),
            'workspace': self.workspace_entry.get().strip(),
            'current_status': self.status_combo.get(),
            'hire_date': self.hire_date_entry.get().strip() or None,
        }

        # Save
        try:
            if self.employee_id:
                # Update
                self._update_employee(data)
            else:
                # Create
                self._create_employee(data)

            self.result = data
            self.destroy()

        except Exception as e:
            ctk.CTkLabel(self, text=f"Error: {str(e)}", text_color="red").pack()

    def _create_employee(self, data):
        """Create new employee."""
        from employee.models import Employee

        hire_date = None
        if data['hire_date']:
            hire_date = datetime.strptime(data['hire_date'], "%Y-%m-%d").date()

        Employee.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'] or None,
            workspace=data['workspace'] or None,
            current_status=data['current_status'],
            hire_date=hire_date
        )

    def _update_employee(self, data):
        """Update existing employee."""
        from employee.models import Employee

        emp = Employee.get_by_id(self.employee_id)

        hire_date = None
        if data['hire_date']:
            hire_date = datetime.strptime(data['hire_date'], "%Y-%m-%d").date()

        emp.first_name = data['first_name']
        emp.last_name = data['last_name']
        emp.role = data['role'] or None
        emp.workspace = data['workspace'] or None
        emp.current_status = data['current_status']
        emp.hire_date = hire_date
        emp.save()

    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.destroy()
```

**Testing Checklist:**
- [ ] Required field validation works
- [ ] Date format validation works
- [ ] Create mode saves to database
- [ ] Edit mode updates database
- [ ] Cancel closes dialog without saving

**Commit Message:**
```
feat: implement employee form dialog with validation

- Add modal dialog for employee create/edit
- Implement form fields (name, role, workspace, status, hire date)
- Add validation for required fields and date format
- Implement save logic (create or update)
- Add cancel button
```

---

#### Step 3.2: Certification Dialogs

**Files:** `src/ui_ctk/dialogs.py`

**Dialogs to implement:**
- `CacesFormDialog`
- `MedicalVisitFormDialog`
- `TrainingFormDialog`

**Implementation Pattern:** (similar to EmployeeFormDialog)

**Testing Checklist:**
- [ ] All form fields validate
- [ ] Dates parse correctly
- [ ] Dropdowns populate
- [ ] Save creates records
- [ ] Employee association works

**Commit Message:**
```
feat: implement certification form dialogs

- Add CACES form dialog (type, number, dates)
- Add medical visit form dialog (date, result, next visit)
- Add training form dialog (name, completion, expiration)
- Implement validation for all forms
- Handle employee association
```

---

#### Step 3.3: Confirmation Dialogs

**File:** `src/ui_ctk/dialogs.py` - `ConfirmDialog`, `ErrorDialog`

**Simple reusable dialogs:**
```python
class ConfirmDialog(ctk.CTkToplevel):
    """Generic confirmation dialog."""

    def __init__(self, parent, title, message):
        super().__init__(parent)

        self.title(title)
        self.geometry("400x200")
        self.result = False

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Message
        ctk.CTkLabel(self, text=message).pack(expand=True, padx=20, pady=20)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="No",
            command=self._on_no,
            fg_color="gray"
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Yes",
            command=self._on_yes,
            fg_color="red"
        ).pack(side="right", padx=10)

    def _on_yes(self):
        """Handle yes button."""
        self.result = True
        self.destroy()

    def _on_no(self):
        """Handle no button."""
        self.result = False
        self.destroy()


class ErrorDialog(ctk.CTkToplevel):
    """Error message dialog."""

    def __init__(self, parent, title, message):
        super().__init__(parent)

        self.title(title)
        self.geometry("400x200")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Message
        ctk.CTkLabel(self, text=message, text_color="red").pack(expand=True, padx=20, pady=20)

        # OK button
        ctk.CTkButton(self, text="OK", command=self.destroy).pack(pady=20)
```

**Commit Message:**
```
feat: implement generic confirmation and error dialogs

- Add reusable ConfirmDialog for yes/no confirmations
- Add ErrorDialog for displaying error messages
- Make dialogs modal with proper window handling
```

---

### Phase 4: Polish & UX (1-2 days)

**Goal:** Improve user experience and visual design

#### Step 4.1: Theme & Styling

**File:** `src/ui_ctk/constants.py`

```python
"""UI constants for styling."""

# Status colors
STATUS_COLORS = {
    'active': '#2CC985',      # Green
    'inactive': '#888888',    # Gray
    'medical_leave': '#FFA500',  # Orange
    'unfit': '#FF4C4C',       # Red
}

# Score colors
SCORE_COLORS = {
    'high': '#2CC985',        # >= 70%
    'medium': '#FFA500',      # 50-69%
    'low': '#FF4C4C',         # < 50%
}

# Alert colors
ALERT_COLORS = {
    'info': '#3498DB',
    'warning': '#FFA500',
    'error': '#FF4C4C',
    'success': '#2CC985',
}

# Spacing
SPACING = {
    'xs': 5,
    'sm': 10,
    'md': 20,
    'lg': 30,
    'xl': 40,
}

# Font sizes
FONT_SIZES = {
    'small': 12,
    'normal': 14,
    'large': 16,
    'xlarge': 18,
    'xxlarge': 24,
    'header': 28,
}
```

**Commit Message:**
```
feat: implement theme constants and styling

- Define status color mapping
- Add score color ranges
- Create alert color palette
- Set spacing constants
- Define font size scale
```

---

#### Step 4.2: Error Handling

**Tasks:**
- Wrap all database operations in try-except
- Show user-friendly error messages
- Handle lock loss gracefully
- Add loading indicators for long operations

**Commit Message:**
```
feat: implement comprehensive error handling

- Add try-except around all database operations
- Display user-friendly error messages
- Handle database connection errors
- Handle lock loss gracefully
- Add validation feedback
```

---

#### Step 4.3: Data Refresh

**Tasks:**
- Add refresh buttons to all views
- Auto-refresh after form save
- Update dashboard stats periodically

**Commit Message:**
```
feat: implement data refresh functionality

- Add refresh buttons to all views
- Auto-refresh views after form operations
- Implement dashboard auto-refresh
- Ensure data consistency across views
```

---

### Phase 5: Testing & Validation (1-2 days)

**Goal:** Ensure application works correctly

#### Step 5.1: Integration Testing

**Test Scenarios:**

1. **Startup Test**
   - [ ] App launches successfully
   - [ ] Database initializes correctly
   - [ ] Lock is acquired
   - [ ] Window displays at correct size

2. **Navigation Test**
   - [ ] All sidebar buttons work
   - [ ] Views switch correctly
   - [ ] No crashes on view changes
   - [ ] Back buttons work

3. **Dashboard Test**
   - [ ] Statistics display accurately
   - [ ] Alerts load correctly
   - [ ] Compliance percentage shows
   - [ ] Empty database handled

4. **Employee List Test**
   - [ ] All employees display
   - [ ] Search filters correctly
   - [ ] Status filter works
   - [ ] Double-click opens detail
   - [ ] Add button opens form

5. **Employee Detail Test**
   - [ ] All data displays
   - [ ] Certifications show correctly
   - [ ] Status indicators work
   - [ ] Back button returns to list
   - [ ] Edit button opens form

6. **Forms Test**
   - [ ] Validation works
   - [ ] Create saves to database
   - [ ] Edit updates database
   - [ ] Cancel doesn't save
   - [ ] Form pre-populates on edit

7. **Lock Test**
   - [ ] Only one instance can run
   - [ ] Second instance shows error
   - [ ] Lock releases on close

8. **CLI Independence Test**
   - [ ] CLI still works
   - [ ] No UI dependencies in CLI

**Commit Message:**
```
test: add comprehensive integration test scenarios

- Define test scenarios for all major features
- Test startup and navigation
- Test data display and interactions
- Test form operations
- Test lock manager
- Verify CLI independence
```

---

#### Step 5.2: Edge Cases

**Test:**
- [ ] Empty database (no employees)
- [ ] Very long names (truncation?)
- [ ] Special characters in inputs (é, ñ, etc.)
- [ ] Future dates (validation)
- [ ] Past dates (validation)
- [ ] Invalid dates (error handling)
- [ ] Database connection lost
- [ ] Window resize (responsive?)
- [ ] Large datasets (100+ employees)

**Commit Message:**
```
fix: handle edge cases and empty states

- Handle empty database gracefully
- Add truncation for long text
- Validate date ranges
- Handle special characters
- Improve error messages
- Add loading states for large datasets
```

---

#### Step 5.3: Performance

**Check:**
- [ ] Employee list loads quickly with 100+ records
- [ ] Dashboard renders instantly
- [ ] No memory leaks (check with prolonged use)
- [ ] Forms open and close quickly

**Commit Message:**
```
perf: optimize rendering and memory usage

- Optimize employee list loading
- Reduce unnecessary redraws
- Fix potential memory leaks
- Improve overall responsiveness
```

---

### Phase 6: Deployment (0.5 day)

**Goal:** Prepare for production use

#### Step 6.1: Final Configuration

**Tasks:**
- [ ] Update `pyproject.toml` with final dependencies
- [ ] Create entry point script
- [ ] Update README with CustomTkinter instructions
- [ ] Add screenshot to README
- [ ] Test on clean environment

**Commit Message:**
```
chore: finalize configuration and documentation

- Update pyproject.toml dependencies
- Add UI entry point to project
- Update README with CustomTkinter instructions
- Add usage documentation
- Test on clean environment
```

---

#### Step 6.2: Create Executable (Optional)

**Tool:** PyInstaller

**Commands:**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "WareflowEMS" --add-data "src;src" src/ui_ctk/app.py
```

**Commit Message:**
```
chore: add PyInstaller configuration for executable

- Add PyInstaller to dev dependencies
- Create spec file for packaging
- Add build instructions to README
```

---

## Testing Strategy

### Unit Testing

Focus on:
- Controller methods (already tested)
- Form validation logic
- Data parsing functions

### Integration Testing

Test user workflows:
1. Add employee → Verify in list
2. Edit employee → Verify changes
3. Add certification → Verify in detail
4. View alerts → Export CSV → Verify data
5. Multiple instances → Verify lock

### Manual Testing Checklist

```
[ ] App starts without errors
[ ] Can navigate between all views
[ ] Can add new employee
[ ] Can edit existing employee
[ ] Can view employee details
[ ] Can add certifications
[ ] Alerts display correctly
[ ] Export works
[ ] Lock prevents multiple instances
[ ] CLI still works
[ ] No console errors
[ ] Window closes cleanly
```

---

## Timeline & Milestones

### MVP (Minimum Viable Product) - 1 Week

**Goal:** Functional app to view and manage employees

- [ ] **Day 1:** Foundation (app shell, navigation)
- [ ] **Day 2:** Dashboard view
- [ ] **Day 3:** Employee list view
- [ ] **Day 4:** Employee detail view
- [ ] **Day 5:** Employee form (create/edit)

**Deliverable:** Working application with core functionality

---

### Complete Implementation - 2 Weeks

**Goal:** Production-ready application

- [ ] **Week 1:** MVP (as above)
- [ ] **Day 6-7:** Certification forms
- [ ] **Day 8:** Alerts view
- [ ] **Day 9:** Polish (styling, error handling)
- [ ] **Day 10:** Testing and bug fixes

**Deliverable:** Production-ready application

---

## Technical Decisions

### Pending Decisions

Before starting implementation, decide on:

1. **Date Picker Implementation**
   - Option A: Use `tkinter.Calendar` (more features)
   - Option B: Simple text entry with validation (simpler)
   - **Recommendation:** Option B for simplicity

2. **Dropdown Values**
   - Option A: Load from database
   - Option B: Hardcode for now
   - **Recommendation:** Option B initially, migrate to A later

3. **Icon Strategy**
   - Option A: Emoji icons (📊👥⚠️) - simplest
   - Option B: Icon font (more professional)
   - **Recommendation:** Option A for MVP

4. **Export Feature Priority**
   - Option A: Implement now
   - Option B: Postpone to v2
   - **Recommendation:** Implement basic CSV export for MVP

5. **Multi-language Support**
   - Option A: French only
   - Option B: i18n ready from start
   - **Recommendation:** Option A (French), keep strings external for later i18n

---

## Risk Management

### Potential Risks

1. **CustomTkinter Learning Curve**
   - **Mitigation:** Start with simple implementations, reference documentation

2. **Database Compatibility**
   - **Mitigation:** Reuse existing tested queries and models

3. **Lock Manager Issues**
   - **Mitigation:** Test early, reuse existing working code

4. **Performance with Large Datasets**
   - **Mitigation:** Implement pagination if needed, test with 100+ records

5. **Cross-platform Compatibility**
   - **Mitigation:** Test on Windows, Mac, Linux before release

---

## Success Criteria

The migration is successful when:

- ✅ Application starts and acquires lock
- ✅ All views are accessible and functional
- ✅ Can create, read, update employees
- ✅ Can add certifications
- ✅ Alerts display correctly
- ✅ Export functionality works
- ✅ CLI remains independent and functional
- ✅ No database corruption
- ✅ Memory usage is reasonable
- ✅ Window closes cleanly

---

## Next Steps

1. **Review this plan** and provide feedback
2. **Answer technical decisions** (date picker, icons, etc.)
3. **Set timeline** (MVP or full implementation?)
4. **Begin Phase 1** when ready

---

**Document Version:** 1.0
**Last Updated:** 2025-01-20
**Author: Claude Sonnet 4.5**
