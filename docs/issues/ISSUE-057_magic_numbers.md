# ISSUE-057: Magic Numbers in Code

## Description

Multiple files contain "magic numbers" - hardcoded numeric values without named constants. This makes code harder to understand, maintain, and modify.

## Affected Files

1. **`src/employee/alerts.py:25`** - Alert threshold days (> 90)
2. **`src/ui_ctk/forms/medical_form.py:351`** - Medical renewal days (> 30)
3. **`src/ui_ctk/forms/caces_form.py:301`** - CACES renewal days (> 30)
4. Various UI dimensions, timeouts, and page sizes throughout codebase

## Examples

### Current Code (Poor)

```python
# src/employee/alerts.py:25
def get_expiring_items(days=90):
    """Get items expiring within 90 days."""
    if days > 90:
        raise ValueError("Days must be 90 or less")
    # ...
```

### Improved Code

```python
# Constants at module level
DEFAULT_ALERT_DAYS = 90
MAX_ALERT_DAYS = 90
MEDICAL_VISIT_RENEWAL_DAYS = 30
CACES_RENEWAL_DAYS = 30

def get_expiring_items(days=DEFAULT_ALERT_DAYS):
    """Get items expiring within default alert period."""
    if days > MAX_ALERT_DAYS:
        raise ValueError(f"Days must be {MAX_ALERT_DAYS} or less")
    # ...
```

## Problems

1. **Unclear Intent:** What does `90` represent? Days? Weeks? Percent?
2. **Hard to Maintain:** Need to change value in multiple places
3. **Inconsistent Values:** Similar logic uses different numbers
4. **No Central Configuration:** Cannot configure without code changes
5. **Difficult Testing:** Hard to test with different threshold values

## Magic Numbers Found

### Alert Thresholds

| File | Line | Value | Meaning |
|------|------|-------|---------|
| `src/employee/alerts.py` | 25 | `90` | Maximum alert days |
| `src/employee/alerts.py` | 30 | `30`, `60`, `90` | Alert warning levels |

### Renewal Periods

| File | Line | Value | Meaning |
|------|------|-------|---------|
| `src/ui_ctk/forms/medical_form.py` | 351 | `30` | Medical visit renewal warning |
| `src/ui_ctk/forms/caces_form.py` | 301 | `30` | CACES renewal warning |

### UI Dimensions

| File | Line | Value | Meaning |
|------|------|-------|---------|
| `src/ui_ctk/constants.py` | Various | `1200`, `800` | Window dimensions |
| `src/ui_ctk/views/*.py` | Various | Various | Padding, margins, sizes |

## Proposed Solution

### Phase 1: Create Constants Module (1 day)

**File: `src/constants/alerts.py`** (New)

```python
"""Alert-related constants."""

# Alert thresholds
DEFAULT_ALERT_DAYS = 90
MAX_ALERT_DAYS = 365
MIN_ALERT_DAYS = 7

# Alert warning levels
ALERT_CRITICAL_DAYS = 30  # Red
ALERT_WARNING_DAYS = 60   # Orange
ALERT_INFO_DAYS = 90      # Yellow

# Renewal periods
MEDICAL_VISIT_RENEWAL_DAYS = 30
CACES_RENEWAL_DAYS = 30
TRAINING_RENEWAL_DAYS = 30

# Display thresholds
ALERT_EXPIRED_DAYS = 0
ALERT_EXPIRING_SOON_DAYS = 30
ALERT_EXPIRING_WARNING_DAYS = 60
ALERT_EXPIRING_FUTURE_DAYS = 90
```

**File: `src/constants/ui.py`** (New)

```python
"""UI-related constants."""

# Window dimensions
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Layout
DEFAULT_PADDING = 10
DEFAULT_MARGIN = 20
BUTTON_SPACING = 5
FORM_SPACING = 10

# Table
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 10

# Dialogs
DIALOG_WIDTH = 500
DIALOG_HEIGHT = 400

# Colors
COLOR_CRITICAL = "#FF0000"
COLOR_WARNING = "#FFA500"
COLOR_INFO = "#FFFF00"
COLOR_SUCCESS = "#00FF00"
```

### Phase 2: Replace Magic Numbers (1-2 days)

**Example 1: `src/employee/alerts.py`**

Before:
```python
def get_expiring_items(days=90):
    if days > 90:
        raise ValueError("Days must be 90 or less")

    if days <= 30:
        level = "critical"
    elif days <= 60:
        level = "warning"
    else:
        level = "info"
```

After:
```python
from constants.alerts import (
    DEFAULT_ALERT_DAYS,
    MAX_ALERT_DAYS,
    ALERT_CRITICAL_DAYS,
    ALERT_WARNING_DAYS,
    ALERT_INFO_DAYS,
)

def get_expiring_items(days=DEFAULT_ALERT_DAYS):
    if days > MAX_ALERT_DAYS:
        raise ValueError(f"Days must be {MAX_ALERT_DAYS} or less")

    if days <= ALERT_CRITICAL_DAYS:
        level = "critical"
    elif days <= ALERT_WARNING_DAYS:
        level = "warning"
    else:
        level = "info"
```

**Example 2: `src/ui_ctk/forms/medical_form.py`**

Before:
```python
if days_until_renewal <= 30:
    show_warning("Medical visit expires soon!")
```

After:
```python
from constants.alerts import MEDICAL_VISIT_RENEWAL_DAYS

if days_until_renewal <= MEDICAL_VISIT_RENEWAL_DAYS:
    show_warning(f"Medical visit expires in {days_until_renewal} days!")
```

### Phase 3: Make Constants Configurable (Optional - 1 day)

**File: `src/config/settings.py`**

```python
from constants.alerts import DEFAULT_ALERT_DAYS

class AlertSettings:
    """Alert configuration settings."""

    # Allow override via config file
    ALERT_DAYS = get_config('alerts.days', DEFAULT_ALERT_DAYS)
    SHOW_EXPIRED = get_config('alerts.show_expired', True)
    WARNING_DAYS = get_config('alerts.warning_days', 30)
```

## Benefits

1. **Clarity:** `MEDICAL_VISIT_RENEWAL_DAYS` is clearer than `30`
2. **Maintainability:** Change value in one place
3. **Consistency:** Same value used everywhere
4. **Testability:** Easy to test with different values
5. **Documentation:** Constants serve as documentation
6. **IDE Support:** Autocomplete shows available constants

## Implementation Order

1. Create constants modules
2. Replace alert threshold numbers
3. Replace renewal period numbers
4. Replace UI dimension numbers
5. Update tests to use constants
6. Run all tests to verify

## Testing

```python
# tests/test_constants.py
def test_alert_constants():
    """Test alert constants are properly defined."""
    from constants.alerts import (
        DEFAULT_ALERT_DAYS,
        ALERT_CRITICAL_DAYS,
        ALERT_WARNING_DAYS,
    )

    assert DEFAULT_ALERT_DAYS == 90
    assert ALERT_CRITICAL_DAYS == 30
    assert ALERT_WARNING_DAYS == 60
    assert ALERT_CRITICAL_DAYS < ALERT_WARNING_DAYS < DEFAULT_ALERT_DAYS

def test_constants_used_in_code():
    """Verify magic numbers removed from code."""
    import ast
    import os

    # Scan source files for magic numbers
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath) as f:
                    tree = ast.parse(f.read())

                # Check for numeric literals (excluding 0, 1, -1)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Num):
                        if node.n not in [0, 1, -1]:
                            print(f"Found magic number {node.n} in {filepath}:{node.lineno}")
```

## Dependencies

- None - this is pure refactoring

## Related Issues

- ISSUE-048: Bare Exception Handlers
- ISSUE-050: Star Imports
- ISSUE-068: Missing Type Hints

## Acceptance Criteria

- [ ] Constants modules created
- [ ] All magic numbers replaced with constants
- [ ] Code still functions correctly
- [ ] All tests pass
- [ ] No numeric literals except 0, 1, -1
- [ ] Constants have descriptive names
- [ ] Constants grouped by category
- [ ] Code is more readable
- [ ] Linter passes

## Estimated Effort

**Total:** 2-3 days
- Create constants modules: 1 day
- Replace magic numbers: 1-2 days
- Testing and verification: 0.5 day

## Notes

This is a code quality improvement that makes the codebase more maintainable. It can be done incrementally, starting with the most critical constants (alert thresholds) and working through the codebase.

## Exceptions

Some numeric literals are acceptable:
- `0`, `1`, `-1` (common in algorithms)
- Mathematical constants (π, e)
- Physics constants
- Values that are self-explanatory in context

## References

- Magic Numbers (anti-pattern): https://en.wikipedia.org/wiki/Magic_number_(programming)
- Constant naming: PEP 8 - https://peps.python.org/pep-0008/#constants
