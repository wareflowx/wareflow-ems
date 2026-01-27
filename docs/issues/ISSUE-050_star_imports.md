# ISSUE-050: Star Imports (Code Smell)

## Description

Multiple files use star imports (`from module import *`), which is a code smell that reduces code clarity, makes namespace pollution unclear, and violates PEP 8 guidelines.

## Affected Files

1. **`src/employee/models.py:7`**
   ```python
   from peewee import *
   ```

2. **`src/database/migration_model.py:10`**
   ```python
   from peewee import *
   ```

3. **`src/lock/models.py:6`**
   ```python
   from peewee import *
   ```

4. **`src/database/version_model.py:10`**
   ```python
   from peewee import *
   ```

## Problems

1. **Unclear Namespace:** Impossible to determine what names are imported without checking the source module
2. **Namespace Pollution:** Imports everything into local namespace, potentially shadowing local variables
3. **IDE Support Poor:** Autocomplete and IDE features work poorly with star imports
4. **PEP 8 Violation:** Explicitly discouraged by Python style guide
5. **Maintenance Burden:** Harder to understand what functions/classes come from where
6. **Refactoring Risk:** Accidentally use imported names thinking they're local

## PEP 8 Guidance

> "Wildcard imports (from module import *) should be avoided, as they make it unclear which names are present in the namespace, confusing both readers and many automated tools."

## Expected Behavior

Use explicit imports that make it clear what is being imported:

**Before:**
```python
from peewee import *

class Employee(Model):
    name = CharField()
    # What is CharField? Unclear without checking peewee
```

**After:**
```python
from peewee import (
    Model,
    CharField,
    IntegerField,
    DateTimeField,
    ForeignKeyField,
    BooleanField,
    TextField,
    DateField,
)

class Employee(Model):
    name = CharField()  # Clear: CharField comes from peewee
```

## Proposed Solution

### Phase 1: Replace Star Imports (1 day)

For each affected file:

1. **Identify all peewee imports used in the file**
2. **Create explicit import statement**
3. **Verify no regressions**
4. **Run tests**

### Example Implementation

**File: `src/employee/models.py`**

**Step 1:** Identify used imports
- Model, CharField, IntegerField, DateTimeField, ForeignKeyField, BooleanField, TextField, DateField, DoesNotExist

**Step 2:** Replace with explicit imports
```python
from peewee import (
    DoesNotExist,
    Model,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    TextField,
)
```

**Step 3:** Verify code still works
- Run all tests
- Manual testing
- Check for undefined names

## Benefits

1. **Clarity:** Immediately clear what each class/function is
2. **IDE Support:** Better autocomplete and navigation
3. **Refactoring:** Easier to refactor when imports are explicit
4. **Code Review:** Easier to review code
5. **Documentation:** Imports serve as documentation of dependencies
6. **Static Analysis:** Better support from linters and type checkers

## Implementation Order

1. `src/employee/models.py` - Most critical, used everywhere
2. `src/database/migration_model.py` - Database layer
3. `src/lock/models.py` - Lock functionality
4. `src/database/version_model.py` - Version tracking

## Testing

After each file is updated:
1. Run unit tests: `uv run pytest tests/`
2. Run integration tests: `uv run pytest tests/integration/`
3. Start application and verify functionality
4. Check for import errors

## Dependencies

- None - this is a pure refactoring task

## Related Issues

- ISSUE-048: Bare Exception Handlers (code quality)
- ISSUE-068: Missing Type Hints (code quality)

## Acceptance Criteria

- [ ] No star imports remain in the codebase
- [ ] All imports use explicit names
- [ ] All tests pass after refactoring
- [ ] Code still functions correctly
- [ ] Linter (ruff) passes without import warnings
- [ ] IDE autocomplete works correctly

## Estimated Effort

**Total:** 1 day
- Identify all used imports: 2 hours
- Replace star imports: 2 hours
- Test and verify: 2 hours
- Code review: 2 hours

## Notes

This is a low-risk refactoring task that can be done incrementally. The benefits are significant for code maintainability and developer experience.

## Exceptions

There are no valid exceptions for star imports in this codebase. All imports should be explicit.

## References

- PEP 8 - Imports: https://peps.python.org/pep-0008/#imports
- Flake8 E401: https://flake8.pycqa.org/en/3.9.0/user/error-codes.html#E401
- Isort import sorting: https://pycqa.github.io/isort/
