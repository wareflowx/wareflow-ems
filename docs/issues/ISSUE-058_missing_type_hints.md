# ISSUE-058: Missing Type Hints

## Description

Many functions and methods lack type hints for parameters and return values. This reduces IDE support, makes code harder to understand, and prevents static type checking.

## Affected Files

### Missing Return Type Hints

1. **`src/cli_main.py:33`** - `def version():`
2. **`src/cli_main.py:44`** - `def cli_main():`
3. **`src/employee/queries.py:10`** - `def get_employees_with_expiring_items(days=30):`
4. **`src/employee/queries.py:94`** - Multiple query functions
5. **`src/employee/queries.py:127,160,205,273`** - More query functions
6. **`src/main_exe.py:11`** - `def setup_sys_path():`

### Missing Parameter Type Hints

- Throughout CLI modules (`src/cli/*.py`)
- Utility functions in `src/utils/`
- Controller methods in `src/controllers/`
- Many form methods in `src/ui_ctk/forms/`

## Impact

1. **Poor IDE Support:** Autocomplete less effective
2. **Harder to Understand:** Need to read code to know types
3. **No Static Checking:** Can't use mypy or similar tools
4. **Refactoring Risk:** Changes may break type contracts
5. **Documentation:** Types serve as documentation

## Examples

### Current Code (Poor)

```python
def get_employees_with_expiring_items(days=30):
    """Get employees with expiring items."""
    results = []
    for employee in Employee.select():
        if has_expiring_items(employee, days):
            results.append(employee)
    return results
```

### Improved Code

```python
from typing import List

def get_employees_with_expiring_items(days: int = 30) -> List[Employee]:
    """
    Get employees with expiring certifications.

    Args:
        days: Number of days to look ahead

    Returns:
        List of employees with expiring items
    """
    results: List[Employee] = []
    for employee in Employee.select():
        if has_expiring_items(employee, days):
            results.append(employee)
    return results
```

## Proposed Solution

### Phase 1: Add Type Hints to Critical Modules (2-3 days)

**Priority modules (start here):**

1. **`src/employee/queries.py`** - All query functions
2. **`src/controllers/*.py`** - All controller methods
3. **`src/utils/validation.py`** - Validation functions
4. **`src/utils/file_validation.py`** - File validation functions

**Example: `src/employee/queries.py`**

```python
from typing import List, Optional
from datetime import date, timedelta
from employee.models import Employee

def get_employees_with_expiring_items(
    days: int = 30
) -> List[Employee]:
    """
    Get employees with items expiring within specified days.

    Args:
        days: Number of days to look ahead (default: 30)

    Returns:
        List of employees with at least one expiring item

    Raises:
        ValueError: If days is negative
    """
    if days < 0:
        raise ValueError("Days must be non-negative")

    threshold = date.today() + timedelta(days=days)
    results: List[Employee] = []

    # ... implementation ...

    return results

def get_employee_by_matricule(
    matricule: str
) -> Optional[Employee]:
    """
    Get employee by matricule.

    Args:
        matricule: Employee matricule (unique identifier)

    Returns:
        Employee if found, None otherwise
    """
    try:
        return Employee.get(Employee.matricule == matricule)
    except Employee.DoesNotExist:
        return None
```

### Phase 2: Add Type Hints to CLI Modules (1-2 days)

**Example: `src/cli/employee.py`**

```python
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def add(
    first_name: str = typer.Option(..., help="First name"),
    last_name: str = typer.Option(..., help="Last name"),
    matricule: str = typer.Option(..., help="Unique matricule"),
    position: str = typer.Option(..., help="Job position"),
    department: str = typer.Option(..., help="Department"),
    status: str = typer.Option("active", help="Employee status"),
) -> None:
    """
    Add a new employee to the database.
    """
    employee = Employee.create(
        first_name=first_name,
        last_name=last_name,
        matricule=matricule,
        position=position,
        department=department,
        status=status,
    )
    typer.echo(f"Employee {employee.full_name} added successfully")

@app.command()
def list(
    status: Optional[str] = typer.Option(None, help="Filter by status"),
    department: Optional[str] = typer.Option(None, help="Filter by department"),
) -> None:
    """
    List employees with optional filters.
    """
    query = Employee.select()

    if status:
        query = query.where(Employee.status == status)
    if department:
        query = query.where(Employee.department == department)

    for employee in query:
        typer.echo(f"{employee.matricule}: {employee.full_name}")
```

### Phase 3: Add Type Hints to Utilities (1 day)

**Example: `src/utils/validation.py`**

```python
from typing import Tuple
import re

def validate_email_address(email: str) -> Tuple[bool, str]:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if email is valid
        - error_message: Empty string if valid, error message if invalid
    """
    if not email:
        return True, ""

    pattern = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    if not pattern.match(email):
        return False, "Invalid email format"

    return True, ""

def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return True, ""

    digits_only = re.sub(r'[^\d+]', '', phone)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False, "Phone number must be 10-15 digits"

    return True, ""
```

### Phase 4: Setup Type Checking (1 day)

**1. Add mypy to project**

```toml
# pyproject.toml
[dependency-groups.dev]
type_check = [
    "mypy>=1.0.0",
]
```

**2. Create mypy configuration**

```ini
# mypy.ini
[mypy]
python_version = 3.14
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True  # Strict mode eventually
ignore_missing_imports = True

[mypy-peewee.*]
ignore_missing_imports = True

[mypy-customtkinter.*]
ignore_missing_imports = True
```

**3. Add type checking to CI**

```yaml
# .github/workflows/ci.yml
- name: Type checking
  run: |
    uv run mypy src/
```

## Type Hint Best Practices

### 1. Use Standard Library Types

```python
from typing import List, Dict, Optional, Tuple, Union

def process_data(
    items: List[str],
    config: Dict[str, Union[str, int]],
    flag: Optional[bool] = None
) -> Tuple[int, str]:
    pass
```

### 2. Use Type Aliases for Complex Types

```python
from typing import Dict, List

# Define type alias
EmployeeData = Dict[str, Union[str, int, date]]

def process_employee(data: EmployeeData) -> None:
    pass
```

### 3. Use Generic Types in Classes

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Repository(Generic[T]):
    def get(self, id: int) -> T:
        pass

    def save(self, item: T) -> None:
        pass
```

### 4. Use Protocol for Duck Typing

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str:
        ...

def display(obj: Renderable) -> None:
    print(obj.render())
```

## Migration Strategy

1. **Start with new code** - All new functions must have type hints
2. **Add to critical paths** - Database, controllers, validation
3. **Incremental addition** - Add to existing code when modifying
4. **Gradual strictness** - Start with mypy in warning mode, enable strict mode eventually

## Dependencies

- **New dependency:** `mypy>=1.0.0`

## Related Issues

- ISSUE-048: Bare Exception Handlers
- ISSUE-050: Star Imports
- ISSUE-057: Magic Numbers

## Acceptance Criteria

- [ ] Type hints added to all query functions
- [ ] Type hints added to all controller methods
- [ ] Type hints added to all validation functions
- [ ] Type hints added to CLI command functions
- [ ] Type hints added to utility functions
- [ ] mypy configuration created
- [ ] Type checking added to CI
- [ ] No new code without type hints
- [ ] All existing code updated with type hints (eventually)

## Estimated Effort

**Total:** 4-6 days
- Critical modules: 2-3 days
- CLI modules: 1-2 days
- Utilities: 1 day
- Setup type checking: 1 day
- Gradual addition to remaining code: Ongoing

## Notes

Adding type hints is a large task that should be done incrementally. Start with critical paths and new code, then gradually add to existing code. The long-term goal is 100% type hint coverage.

## Target Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Functions with type hints | ~20% | 100% |
| Methods with type hints | ~15% | 100% |
| mypy errors | N/A | 0 |
| Type coverage | 20% | 100% |

## References

- Python type hints: https://docs.python.org/3/library/typing.html
- mypy documentation: https://mypy.readthedocs.io/
- Type hints cheat sheet: https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
