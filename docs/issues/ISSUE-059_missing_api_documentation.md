# ISSUE-059: Missing API Documentation

## Description

The project lacks comprehensive API documentation. Public functions, classes, and methods in the `src/` directory have minimal or no docstrings, making the codebase difficult to understand and maintain.

## Current State

### What Exists:
- Basic docstrings on some model classes
- Minimal docstrings on some functions
- No API documentation for public modules
- No generated documentation (Sphinx, MkDocs, etc.)

### What's Missing:
- Detailed docstrings for public functions
- Parameter descriptions with types
- Return value descriptions
- Exception documentation
- Usage examples
- Module-level documentation
- Generated HTML documentation

## Impact

1. **Hard to Understand:** Need to read code to understand usage
2. **Onboarding Difficult:** New developers struggle to contribute
3. **Maintenance Burden:** Hard to remember function details
4. **No Reference:** No quick reference for APIs
5. **Poor Developer Experience:** IDE shows limited help

## Expected Documentation Standards

### 1. Module Docstrings

Every module should have a docstring explaining its purpose:

```python
"""
Employee model and business logic.

This module contains the Employee model and related business logic
for managing employee records, including:
- Employee CRUD operations
- Relationship management (CACES, medical visits, trainings)
- Employee calculations (age, seniority, etc.)

Example:
    >>> from employee.models import Employee
    >>> emp = Employee.get_by_id(1)
    >>> print(emp.full_name)
    "John Doe"
"""
```

### 2. Class Docstrings

```python
class ExportController:
    """
    Controller for Excel export operations.

    This controller manages the export of employee data to Excel format,
    including employees, CACES certifications, medical visits, and training records.

    Attributes:
        exporter: DataExporter instance for performing exports
        exporting: Boolean flag indicating if export is in progress

    Example:
        >>> controller = ExportController()
        >>> controller.export_employees(
        ...     output_path="employees.xlsx",
        ...     employees=employee_list,
        ...     include_caces=True
        ... )
    """
```

### 3. Function/Method Docstrings

Use Google style docstrings:

```python
def get_employees_with_expiring_items(days: int = 30) -> list[Employee]:
    """
    Get employees with expiring certifications or medical visits.

    This function queries the database for employees who have at least one
    certification or medical visit that will expire within the specified number of days.

    Args:
        days: Number of days to look ahead from today. Must be positive.
            Default is 30 days.

    Returns:
        List of Employee objects with at least one expiring item.
        Returns empty list if no employees have expiring items.

    Raises:
        ValueError: If days is negative or zero.

    Example:
        >>> from employee.queries import get_employees_with_expiring_items
        >>> expiring = get_employees_with_expiring_items(days=60)
        >>> print(f"Found {len(expiring)} employees with expiring items")
        Found 15 employees with expiring items
    """
    if days <= 0:
        raise ValueError("Days must be positive")

    # ... implementation ...
```

## Proposed Solution

### Phase 1: Add Module Docstrings (2-3 days)

**Modules to document:**

1. **`src/employee/models.py`** - Employee models
2. **`src/employee/queries.py`** - Employee queries
3. **`src/employee/calculations.py`** - Employee calculations
4. **`src/controllers/*.py`** - All controllers
5. **`src/utils/validation.py`** - Validation utilities
6. **`src/utils/file_validation.py`** - File validation
7. **`src/export/data_exporter.py`** - Export functionality
8. **`src/excel_import/excel_importer.py`** - Import functionality

**Template:**

```python
"""
[One-line summary of module purpose].

[Detailed description of module functionality and what it provides].

Key Features:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Classes:
- [ClassName]: [Brief description]

Functions:
- [function_name]: [Brief description]

Example:
    [Usage example]

See Also:
- [Related module or documentation]
"""
```

### Phase 2: Add Class Docstrings (1-2 days)

For each public class, add comprehensive docstring:

**Template:**

```python
class ClassName:
    """
    [One-line summary of class purpose].

    [Detailed description of what the class does and how to use it].

    This class is responsible for [what it does]. It should be used when
    [when to use it].

    Attributes:
        attr1: Description of attribute1
        attr2: Description of attribute2

    Args:
        param1: Description of parameter1
        param2: Description of parameter2

    Raises:
        ErrorType: Description of when this error is raised

    Example:
        >>> obj = ClassName(param1="value", param2="value")
        >>> obj.method()
        result

    Note:
        [Any important notes about usage]

    Warning:
        [Any warnings about usage or behavior]
    """
```

### Phase 3: Add Function/Method Docstrings (2-3 days)

For each public function/method, add comprehensive docstring:

**Priority:**
1. All controller methods
2. All query functions
3. All validation functions
4. All export/import functions
5. Public utility functions

### Phase 4: Setup Documentation Generation (1-2 days)

**1. Install Sphinx**

```toml
# pyproject.toml
[dependency-groups.docs]
sphinx = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=2.0.0",
    "sphinx-autodoc-typehints>=2.0.0",
]
```

**2. Create Sphinx Configuration**

```python
# docs/conf.py
project = 'Wareflow EMS'
copyright = '2024, Wareflow'
author = 'Wareflow'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

typehints_defaults = 'comma'
```

**3. Create API Documentation Files**

```rst
# docs/api/reference.rst
API Reference
=============

.. toctree::
   :maxdepth: 4

   employee
   controllers
   utils
   export
   import
```

```rst
# docs/api/employee.rst
Employee Module
===============

Models
------

.. automodule:: employee.models
    :members:
    :undoc-members:
    :show-inheritance:

Queries
-------

.. automodule:: employee.queries
    :members:
    :undoc-members:

Calculations
------------

.. automodule:: employee.calculations
    :members:
    :undoc-members:
```

**4. Build Documentation**

```bash
cd docs
sphinx-build -b html api build/html
```

### Phase 5: Add to CI (0.5 day)

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths: ['src/**', 'docs/**']

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: |
          pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
      - name: Build documentation
        run: |
          cd docs
          sphinx-build -b html api build/html
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build/html
```

## Documentation Standards

### Google Style (Recommended)

```python
def function(arg1, arg2):
    """Summary line.

    Extended description of function.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ErrorType: Description of when error is raised
    """
```

### reStructuredText Style

```python
def function(arg1, arg2):
    """Summary line.

    Extended description of function.

    :param arg1: Description of arg1
    :param arg2: Description of arg2
    :returns: Description of return value
    :raises ErrorType: Description of when error is raised
    """
```

## Dependencies

- **New dependencies (docs):**
  - `sphinx>=7.0.0`
  - `sphinx-rtd-theme>=2.0.0`
  - `sphinx-autodoc-typehints>=2.0.0`

## Related Issues

- ISSUE-041: No User Documentation
- ISSUE-042: No Troubleshooting Guide
- ISSUE-068: Missing Type Hints

## Acceptance Criteria

- [ ] All public modules have docstrings
- [ ] All public classes have docstrings
- [ ] All public functions have docstrings
- [ ] Docstrings follow Google style or reStructuredText
- [ ] Docstrings include examples
- [ ] Docstrings document parameters
- [ ] Docstrings document return values
- [ ] Docstrings document exceptions
- [ ] Sphinx configuration created
- [ ] API documentation builds successfully
- [ ] Documentation deployed to GitHub Pages
- [ ] CI builds and deploys documentation

## Estimated Effort

**Total:** 5-7 days
- Add module docstrings: 2-3 days
- Add class docstrings: 1-2 days
- Add function docstrings: 2-3 days
- Setup Sphinx and CI: 1-2 days

## Notes

This is a large task that should be done incrementally. Start with critical modules (models, controllers, queries) and work through the codebase systematically. Documentation should be updated whenever code changes.

## Documentation Quality Checklist

For each docstring:
- [ ] Summary line (one sentence)
- [ ] Extended description (if needed)
- [ ] All parameters documented
- [ ] Return value documented
- [ ] Exceptions documented
- [ ] Usage example included (for complex functions)
- [ ] Notes or warnings (if applicable)

## References

- Sphinx documentation: https://www.sphinx-doc.org/
- Napoleon extension: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
- Google Python Style Guide: http://google.github.io/styleguide/pyguide.html#381-docstrings
- PEP 257 (Docstring Conventions): https://peps.python.org/pep-0257/
- reStructuredText Primer: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
