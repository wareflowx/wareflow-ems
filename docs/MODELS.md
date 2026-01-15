# Data Models Design

This document details the design and implementation strategy for Peewee ORM models in the Warehouse Employee Management System.

## Overview

The models follow an **entity-oriented** approach where:
- Models contain their own business logic (classmethods, instance methods, properties)
- Relationships are defined with foreign keys and back-references
- Calculated properties are computed on-demand
- Class methods provide domain-specific queries

---

## 1. Database Configuration

### File: `src/database/connection.py`

### Purpose

Create a singleton Database instance configured for SQLite with Write-Ahead Logging (WAL) mode enabled for optimal network share performance.

### Implementation

```python
from peewee import SqliteDatabase
from pathlib import Path

# IMPORTANT: Enable foreign_keys in SQLite to ensure CASCADE delete works
# SQLite by default has ON DELETE disabled, which can cause data integrity issues
database = SqliteDatabase(None, pragmas={'foreign_keys': 1})

def init_database(db_path: Path) -> None:
    """
    Initialize database connection with WAL mode and optimal PRAGMAs.

    Args:
        db_path: Path to SQLite database file
    """
    database.init(db_path)

    # Enable WAL mode for better concurrent read performance
    database.execute_sql('PRAGMA journal_mode=WAL')
    database.execute_sql('PRAGMA synchronous=NORMAL')
    database.execute_sql('PRAGMA busy_timeout=5000')

    # Create all tables
    database.create_tables([
        Employee,
        Caces,
        MedicalVisit,
        OnlineTraining,
        AppLock,
    ], safe=True)

def get_database() -> SqliteDatabase:
    """Return the database instance."""
    return database
```

### Why WAL Mode?

| Feature | Without WAL | With WAL |
|---------|-------------|----------|
| Concurrent readers during write | No | Yes |
| File locking behavior | Aggressive | Less aggressive |
| Network share performance | Slower | Faster |
| Crash recovery | Manual | Automatic |

### PRAGMA Configuration Rationale

- **`journal_mode=WAL`**: Write-Ahead Logging for concurrent reads
- **`foreign_keys=1`**: **CRITICAL** - Enable referential integrity. Without this, CASCADE delete will NOT work in SQLite and data can be silently relinked
- **`synchronous=NORMAL`**: Balance between safety and performance
- **`busy_timeout=5000`**: Wait 5 seconds before failing on lock

---

## 2. Employee Model

### File: `src/employee/models.py`

### Model Structure

```python
from peewee import *
from datetime import date, datetime
from employee.constants import (
    EmployeeStatus,
    ContractType,
)

class Employee(Model):
    """Core employee entity with business logic."""

    # Primary Key - UUIDField is native in Peewee
    # In SQLite/MySQL it's stored as VARCHAR, in Postgres as native UUID
    id = UUIDField(primary=True)

    # Identification
    external_id = CharField(null=True, index=True, unique=True)  # WMS reference
    first_name = CharField()
    last_name = CharField()

    # Employment Status
    current_status = CharField()  # Enum: 'active', 'inactive'
    workspace = CharField()
    role = CharField()
    contract_type = CharField()  # Enum: 'CDI', 'CDD', 'Interim', 'Alternance'

    # Employment Dates
    entry_date = DateField()

    # Optional
    avatar_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'employees'

    # ========== COMPUTED PROPERTIES ==========

    @property
    def full_name(self) -> str:
        """Complete employee name for display."""
        return f"{self.first_name} {self.last_name}"

    @property
    def seniority(self) -> int:
        """Complete years of service."""
        return (date.today() - self.entry_date).days // 365

    @property
    def is_active(self) -> bool:
        """Convenience boolean for active status."""
        return self.current_status == EmployeeStatus.ACTIVE

    # ========== CLASS METHODS (QUERIES) ==========

    @classmethod
    def active(cls):
        """Get all active employees."""
        return cls.select().where(cls.current_status == EmployeeStatus.ACTIVE)

    @classmethod
    def inactive(cls):
        """Get all inactive employees."""
        return cls.select().where(cls.current_status == EmployeeStatus.INACTIVE)

    @classmethod
    def by_workspace(cls, workspace: str):
        """Get employees by workspace assignment."""
        return cls.select().where(cls.workspace == workspace)

    @classmethod
    def by_role(cls, role: str):
        """Get employees by job role."""
        return cls.select().where(cls.role == role)

    @classmethod
    def by_contract_type(cls, contract_type: str):
        """Get employees by contract type."""
        return cls.select().where(cls.contract_type == contract_type)

    # Note: Complex multi-table queries like with_expiring_certifications
    # will be implemented in employee/queries.py to avoid circular imports

    # ========== INSTANCE METHODS ==========

    def add_caces(self, kind: str, completion_date: date, document_path: str):
        """Create a CACES certification for this employee."""
        return Caces.create(
            employee=self,
            kind=kind,
            completion_date=completion_date,
            document_path=document_path
        )

    def add_medical_visit(self, visit_type: str, visit_date: date,
                         result: str, document_path: str):
        """Create a medical visit record for this employee."""
        return MedicalVisit.create(
            employee=self,
            visit_type=visit_type,
            visit_date=visit_date,
            result=result,
            document_path=document_path
        )

    def add_training(self, title: str, completion_date: date,
                    validity_months: int, certificate_path: str):
        """Create an online training record for this employee."""
        return OnlineTraining.create(
            employee=self,
            title=title,
            completion_date=completion_date,
            validity_months=validity_months,
            certificate_path=certificate_path
        )

    # ========== HOOKS (Not validate() method) ==========

    def before_save(self):
        """Validation logic using Peewee hooks."""
        if self.entry_date > date.today():
            raise ValueError("Entry date cannot be in the future")

    def save(self, force_insert=False, only=None):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.now()
        return super().save(force_insert=force_insert, only=only)
```

### Relationships

```python
# Back-references are AUTOMATICALLY created by ForeignKeyField
# No need to declare them in Employee model

# Access related objects:
employee = Employee.get_by_id(123)
caces_list = employee.caces           # Auto-created from Caces.employee ForeignKey
visits = employee.medical_visits       # Auto-created from MedicalVisit.employee ForeignKey
trainings = employee.trainings         # Auto-created from OnlineTraining.employee ForeignKey
```

### Relationship Summary

```
Employee (1) ----< (N) Caces
Employee (1) ----< (N) MedicalVisit
Employee (1) ----< (N) OnlineTraining
```

---

## 3. Caces Model

### File: `src/employee/models.py` (continuing)

### Model Structure

```python
from dateutil.relativedelta import relativedelta

class Caces(Model):
    """
    CACES certification (Certificat d'Aptitude à la Conduite En Sécurité).

    French certification for operating heavy machinery and equipment.
    """

    id = UUIDField(primary=True)
    employee = ForeignKeyField(Employee, backref='caces', on_delete='CASCADE')

    # Certification Details
    kind = CharField()  # e.g., 'R489-1A', 'R489-1B', 'R489-3', 'R489-4'
    completion_date = DateField()

    # Calculated at creation time
    expiration_date = DateField(index=True)

    # Document
    document_path = CharField()

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'caces'
        indexes = (
            (('employee', 'expiration_date'), False),  # Composite index
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration (negative if already expired)."""
        return (self.expiration_date - date.today()).days

    @property
    def status(self) -> str:
        """
        Human-readable status.

        Returns:
            'expired': Already expired
            'critical': Expires within 30 days
            'warning': Expires within 60 days
            'valid': More than 60 days remaining
        """
        if self.is_expired:
            return "expired"
        elif self.days_until_expiration < 30:
            return "critical"
        elif self.days_until_expiration < 60:
            return "warning"
        else:
            return "valid"

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, kind: str, completion_date: date) -> date:
        """
        Calculate expiration date based on CACES kind.

        Rules:
        - R489-1A, R489-1B, R489-3, R489-4: 5 years validity
        - Other certifications: 10 years validity

        Args:
            kind: CACES certification type
            completion_date: Date when certification was obtained

        Returns:
            Expiration date (handles leap years correctly)
        """
        if kind in ['R489-1A', 'R489-1B', 'R489-3', 'R489-4']:
            years = 5
        else:
            years = 10

        # Use relativedelta to handle leap years correctly
        # This is more accurate than timedelta(days=years*365)
        return completion_date + relativedelta(years=years)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get all certifications expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.expiration_date <= threshold) &
            (cls.expiration_date >= date.today())
        )

    @classmethod
    def expired(cls):
        """Get all expired certifications."""
        return cls.select().where(cls.expiration_date < date.today())

    @classmethod
    def by_kind(cls, kind: str):
        """Get certifications by type."""
        return cls.select().where(cls.kind == kind)

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration(
                self.kind,
                self.completion_date
            )
```

### CACES Types

Standard French CACES certifications:
- **R489-1A**: Forklift truck with upright (porté-à-faux)
- **R489-1B**: Forklift truck with retractable mast (mât rétractable)
- **R489-3**: Heavy forklift ≥ 6 tons
- **R489-4**: Heavy retractable mast forklift ≥ 6 tons
- **R489-5**: Side-loading forklift

---

## 4. MedicalVisit Model

### File: `src/employee/models.py` (continuing)

### Model Structure

```python
class MedicalVisit(Model):
    """
    Occupational health visit record.

    French labor law requires periodic medical examinations for workers.
    """

    id = UUIDField(primary=True)
    employee = ForeignKeyField(Employee, backref='medical_visits', on_delete='CASCADE')

    # Visit Details
    visit_type = CharField()  # 'initial', 'periodic', 'recovery'
    visit_date = DateField()

    # Calculated expiration
    expiration_date = DateField(index=True)

    # Visit Result
    result = CharField()  # 'fit', 'unfit', 'fit_with_restrictions'

    # Document
    document_path = CharField()

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'medical_visits'
        indexes = (
            (('employee', 'expiration_date'), False),
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_expired(self) -> bool:
        """Check if medical clearance is expired."""
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration."""
        return (self.expiration_date - date.today()).days

    @property
    def is_fit(self) -> bool:
        """Convenience: is employee fit for work?"""
        return self.result == 'fit'

    @property
    def has_restrictions(self) -> bool:
        """Does this visit have work restrictions?"""
        return self.result == 'fit_with_restrictions'

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, visit_type: str, visit_date: date) -> date:
        """
        Calculate medical visit expiration based on type.

        Rules:
        - Initial visit: 2 years
        - Periodic visit: 2 years
        - Recovery visit: 1 year

        Args:
            visit_type: Type of medical visit
            visit_date: Date when visit occurred

        Returns:
            Expiration date (handles leap years correctly)
        """
        if visit_type == 'recovery':
            years = 1
        else:  # initial or periodic
            years = 2

        # Use relativedelta to handle leap years correctly
        return visit_date + relativedelta(years=years)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get medical visits expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.expiration_date <= threshold) &
            (cls.expiration_date >= date.today())
        )

    @classmethod
    def unfit_employees(cls):
        """Get employees with unfit medical visits."""
        return (Employee
                .select(Employee, cls)
                .join(cls)
                .where(cls.result == 'unfit'))

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration(
                self.visit_type,
                self.visit_date
            )
```

---

## 5. OnlineTraining Model

### File: `src/employee/models.py` (continuing)

### Model Structure

```python
class OnlineTraining(Model):
    """
    Online training completion record.

    Some trainings have expiration dates, others are permanent.
    """

    id = UUIDField(primary=True)
    employee = ForeignKeyField(Employee, backref='trainings', on_delete='CASCADE')

    # Training Details
    title = CharField()
    completion_date = DateField()

    # Validity (NULL = permanent, no expiration)
    validity_months = IntegerField(null=True)

    # Calculated expiration (NULL if permanent)
    expiration_date = DateField(null=True, index=True)

    # Certificate (optional)
    certificate_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'online_trainings'
        indexes = (
            (('employee', 'expiration_date'), False),
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def expires(self) -> bool:
        """Does this training expire?"""
        return self.validity_months is not None

    @property
    def is_expired(self) -> bool:
        """Check if training is expired (only if it expires)."""
        if not self.expires:
            return False
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int | None:
        """Days until expiration, or None if permanent."""
        if not self.expires:
            return None
        return (self.expiration_date - date.today()).days

    @property
    def status(self) -> str:
        """Human-readable status."""
        if not self.expires:
            return "permanent"
        elif self.is_expired:
            return "expired"
        elif self.days_until_expiration < 30:
            return "critical"
        elif self.days_until_expiration < 60:
            return "warning"
        else:
            return "valid"

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, completion_date: date, validity_months: int | None) -> date | None:
        """
        Calculate training expiration date.

        If validity_months is None, training has no expiration (permanent).

        Args:
            completion_date: Date when training was completed
            validity_months: Number of months training is valid, or None for permanent

        Returns:
            Expiration date, or None for permanent trainings
        """
        if validity_months is None:
            return None

        # Use relativedelta for accurate month addition
        return completion_date + relativedelta(months=validity_months)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get trainings expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.expiration_date.is_null(False)) &
            (cls.expiration_date <= threshold) &
            (cls.expiration_date >= date.today())
        )

    @classmethod
    def permanent(cls):
        """Get all permanent (non-expiring) trainings."""
        return cls.select().where(cls.validity_months.is_null(True))

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if self.expiration_date is None and self.validity_months is not None:
            self.expiration_date = self.calculate_expiration(
                self.completion_date,
                self.validity_months
            )
```

---

## 6. AppLock Model

### File: `src/lock/models.py`

### Model Structure

```python
class AppLock(Model):
    """
    Application lock for concurrent access control.

    Ensures only one user can edit data at a time on shared network drives.
    Uses heartbeat mechanism to detect stale locks from crashed applications.
    """

    id = UUIDField(primary=True)

    # Lock holder identification
    hostname = CharField(index=True)  # Machine name
    username = CharField(null=True)   # Optional: user name

    # Timestamps
    locked_at = DateTimeField(default=datetime.now, index=True)
    last_heartbeat = DateTimeField(default=datetime.now, index=True)

    # Process identification
    process_id = IntegerField()  # PID for debugging

    # Metadata
    app_version = CharField(null=True)  # For debugging/version tracking

    class Meta:
        database = database
        table_name = 'app_locks'

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_stale(self, timeout_minutes=2) -> bool:
        """
        Check if lock is stale (no recent heartbeat).

        Args:
            timeout_minutes: Minutes of inactivity before considering lock stale.
                            Default: 2 minutes (allows 4 missed heartbeats)

        Returns:
            True if lock is stale and can be safely overridden
        """
        threshold = datetime.now() - timedelta(minutes=timeout_minutes)
        return self.last_heartbeat < threshold

    @property
    def age_seconds(self) -> int:
        """Age of lock in seconds since acquisition."""
        return int((datetime.now() - self.locked_at).total_seconds())

    @property
    def heartbeat_age_seconds(self) -> int:
        """Seconds since last heartbeat."""
        return int((datetime.now() - self.last_heartbeat).total_seconds())

    # ========== CLASS METHODS ==========

    @classmethod
    def acquire(cls, hostname: str, username: str | None, pid: int,
               app_version: str | None = None) -> 'AppLock':
        """
        Acquire application lock.

        Fails if an active lock already exists.

        Args:
            hostname: Machine name of lock holder
            username: Optional user name
            pid: Process ID
            app_version: Optional application version

        Returns:
            AppLock instance

        Raises:
            RuntimeError: If lock is already held by active host
        """
        # Check for existing active lock
        existing = cls.get_active_lock()
        if existing and not existing.is_stale:
            raise RuntimeError(
                f"Lock is held by {existing.hostname} "
                f"(since {existing.locked_at.strftime('%H:%M:%S')})"
            )

        # Remove stale lock if exists
        if existing:
            existing.delete_instance()

        # Create new lock
        return cls.create(
            hostname=hostname,
            username=username,
            process_id=pid,
            app_version=app_version
        )

    @classmethod
    def release(cls, hostname: str, pid: int) -> bool:
        """
        Release lock (only if owned by caller).

        Args:
            hostname: Must match lock holder's hostname
            pid: Must match lock holder's process ID

        Returns:
            True if lock was released, False if not owned by caller
        """
        lock = cls.get_active_lock()
        if not lock:
            return False

        if lock.hostname != hostname or lock.process_id != pid:
            return False

        lock.delete_instance()
        return True

    @classmethod
    def refresh_heartbeat(cls, hostname: str, pid: int) -> bool:
        """
        Update heartbeat timestamp to keep lock alive.

        Should be called every 30 seconds while holding lock.

        Args:
            hostname: Must match lock holder's hostname
            pid: Must match lock holder's process ID

        Returns:
            True if heartbeat updated, False if not lock owner
        """
        lock = cls.get_active_lock()
        if not lock:
            return False

        if lock.hostname != hostname or lock.process_id != pid:
            return False

        lock.last_heartbeat = datetime.now()
        lock.save(only=[AppLock.last_heartbeat])  # Only update heartbeat field
        return True

    @classmethod
    def get_active_lock(cls) -> 'AppLock | None':
        """
        Get current active lock, or None if no active lock exists.

        Returns None if lock is stale (considered inactive).
        """
        lock = cls.select().order_by(cls.locked_at.desc()).first()
        if not lock:
            return None

        # Return None if lock is stale
        if lock.is_stale:
            return None

        return lock
```

### Heartbeat Mechanism

The locking system uses a heartbeat to detect crashed applications:

1. **Lock acquisition**: Create AppLock record with current timestamp
2. **Heartbeat**: Every 30 seconds, update `last_heartbeat` field
3. **Stale detection**: If `last_heartbeat` > 2 minutes ago (4 missed heartbeats), lock is considered stale
4. **Lock override**: Stale locks can be safely overridden by new users

**Frequency Rationale**:
- Heartbeat every 30 seconds: Lightweight network traffic
- Timeout after 2 minutes: Allows for brief network hiccups (4 missed heartbeats)
- Balance between quick crash detection and tolerance of temporary network issues

---

## 7. Constants and Enums

### File: `src/employee/constants.py`

```python
"""Employee-related constants and enums."""

class EmployeeStatus:
    """Employee employment status."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ALL = [ACTIVE, INACTIVE]

class ContractType:
    """Employment contract types."""
    CDI = 'CDI'
    CDD = 'CDD'
    INTERIM = 'Interim'
    ALTERNANCE = 'Alternance'
    ALL = [CDI, CDD, INTERIM, ALTERNANCE]

class VisitType:
    """Medical visit types."""
    INITIAL = 'initial'
    PERIODIC = 'periodic'
    RECOVERY = 'recovery'
    ALL = [INITIAL, PERIODIC, RECOVERY]

class VisitResult:
    """Medical visit results."""
    FIT = 'fit'
    UNFIT = 'unfit'
    FIT_WITH_RESTRICTIONS = 'fit_with_restrictions'
    ALL = [FIT, UNFIT, FIT_WITH_RESTRICTIONS]

# Standard French CACES certifications
CACES_TYPES = [
    'R489-1A',  # Forklift with upright (porté-à-faux)
    'R489-1B',  # Forklift with retractable mast (mât rétractable)
    'R489-3',   # Heavy forklift ≥ 6 tons
    'R489-4',   # Heavy retractable mast forklift ≥ 6 tons
    'R489-5',   # Side-loading forklift
]

# CACES validity periods in years (configurable in future)
CACES_VALIDITY_YEARS = {
    'R489-1A': 5,
    'R489-1B': 5,
    'R489-3': 5,
    'R489-4': 5,
    'R489-5': 10,  # Different validity period
}

# Medical visit validity periods in years
VISIT_VALIDITY_YEARS = {
    'initial': 2,
    'periodic': 2,
    'recovery': 1,
}

# Default workspaces (configurable in config.json)
DEFAULT_WORKSPACES = [
    'Quai',
    'Zone A',
    'Zone B',
    'Bureau',
]

# Default roles (configurable in config.json)
DEFAULT_ROLES = [
    'Préparateur',
    'Réceptionnaire',
    'Cariste',
]
```

---

## 8. N+1 Query Performance

### Problem

Peewee's default lazy loading can cause N+1 query problems:

```python
# ❌ BAD: N+1 queries
employees = Employee.select()
for emp in employees:
    print(emp.caces)  # Each access triggers a new query!
```

### Solution: Use prefetch() for relations

```python
# ✅ GOOD: Single query with prefetch
from peewee import prefetch

employees = Employee.select()
# Prefetch related Caces, MedicalVisit, OnlineTraining
employees_with_data = prefetch(employees, Caces, MedicalVisit, OnlineTraining)

for emp in employees_with_data:
    print(emp.caces)  # Already loaded, no extra query!
```

### Solution: Use join() when filtering

```python
# ✅ GOOD: Join to filter by related data
query = (Employee
         .select(Employee, Caces)
         .join(Caces)
         .where(Caces.kind == 'R489-1A'))
```

**Note**: Document these patterns in `employee/queries.py` when implemented.

---

## 9. CASCADE Delete Warning

⚠️ **IMPORTANT**: CASCADE delete is configured on all foreign keys.

**What this means**:
- When you delete an Employee, ALL their CACES, MedicalVisit, and OnlineTraining records are automatically deleted
- This cannot be undone
- No confirmation is asked by the database

**Risk**:
- Accidental employee deletion = permanent loss of all certification and medical history

**Mitigation strategies**:
1. **UI-level confirmation**: Always show a warning dialog before deleting
2. **Soft delete consideration**: Consider adding `deleted_at` column instead of hard delete
3. **Backup strategy**: Regular database backups for recovery
4. **Audit trail**: Log all deletions with timestamp and user

**Alternative**: If you want to prevent accidental deletion, remove `on_delete='CASCADE'` and handle orphaned records manually or add application-level checks.

---

## 10. Implementation Order

Models should be implemented in this order:

1. **`src/database/connection.py`**
   - Database singleton with `pragmas={'foreign_keys': 1}`
   - `init_database()` function
   - PRAGMA configuration

2. **`src/employee/constants.py`**
   - All enum classes
   - CACES types and validity periods
   - Default values

3. **`src/employee/models.py`**
   - Employee model (no dependencies)
   - Caces model (depends on Employee)
   - MedicalVisit model (depends on Employee)
   - OnlineTraining model (depends on Employee)

4. **`src/lock/models.py`**
   - AppLock model (independent)

5. **Tests**
   - Verify table creation
   - Test relationships
   - Test computed properties
   - Test class methods
   - Test CASCADE delete behavior
   - Test lock heartbeat mechanism

---

## 11. Design Decisions

### Why UUID instead of Auto-increment?

- **Security**: UUIDs are not predictable, preventing enumeration attacks
- **Distribution**: Safe for distributed systems (future-proof)
- **Collision resistance**: Virtually impossible to collide
- **Standard**: Modern best practice for primary keys
- **Peewee native**: `UUIDField` is built into Peewee (stored as VARCHAR in SQLite)

### Why CASCADE delete?

- **Referential integrity**: Prevent orphaned records
- **Clean deletion**: Deleting employee removes all related data
- **Simplicity**: No need for manual cleanup
- **Risk**: Accidental deletion loses all related data (see warning above)

**Alternative**: Soft delete with `deleted_at` column if accidental deletion is a concern.

### Why hard delete (not soft delete)?

- **Simplicity**: No need for additional `is_deleted` flag
- **Privacy**: GDPR compliance (actually remove data)
- **Performance**: Smaller tables, simpler queries
- **Use case**: Rarely need to "restore" deleted employees

### Why timezone-naive timestamps?

- **Desktop app**: Single timezone per deployment
- **Simplicity**: No timezone conversion complexity
- **SQLite**: Limited timezone support
- **Use case**: All users in same timezone (warehouse)

### Why relativedelta over timedelta for dates?

- **Accuracy**: `timedelta(days=365*5)` doesn't account for leap years
- **Correctness**: `relativedelta(years=5)` handles leap years properly
- **Example**: Feb 29, 2020 + 5 years = Feb 28, 2025 (not an error)
- **Dependency**: Requires `python-dateutil` package

### Why heartbeats every 30s with 2-minute timeout?

- **Network tolerance**: Allows 4 missed heartbeats before timeout
- **Quick crash detection**: 2 minutes is reasonable for stale lock detection
- **Lightweight**: 30-second heartbeat is minimal network traffic
- **Balance**: Not too aggressive (prevents false positives), not too slow

---

## 12. Dependencies Required

Add to `pyproject.toml`:

```toml
dependencies = [
    "peewee>=3.17.0",
    "python-dateutil>=2.8.0",  # For relativedelta (accurate date calculations)
    # ... other dependencies
]
```

---

## 13. Next Steps After Models

Once models are implemented:

1. **`src/employee/queries.py`**
   - Complex multi-table queries (e.g., `with_expiring_certifications`)
   - Optimized queries using `prefetch()` and `join()`
   - Query builders for common patterns

2. **`src/employee/calculations.py`**
   - Alert calculation logic
   - Seniority calculations (if more complex than model property)
   - Status determination functions

3. **`src/employee/validators.py`**
   - Custom Peewee validators using `peewee.ValidationError`
   - Business rule validation
   - Data integrity checks

4. **`src/lock/manager.py`**
   - Lock management logic (wraps AppLock model)
   - Heartbeat timer implementation
   - Stale lock cleanup routine

5. **Tests**
   - Unit tests for all models
   - Integration tests for queries with `prefetch()`
   - Lock mechanism tests (heartbeat, stale detection)
   - CASCADE delete behavior tests
