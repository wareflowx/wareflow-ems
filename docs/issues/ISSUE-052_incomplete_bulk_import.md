# ISSUE-052: Incomplete Bulk Import Functionality

## Description

The bulk Excel import feature exists but is incomplete (approximately 50% done). This is critical for initial system setup with 50+ employees, as manual data entry would be impractical and error-prone.

## Affected Files

- **`src/excel_import/excel_importer.py`** - Main import logic (partial)
- **`src/ui_ctk/views/import_view.py`** - Import UI (partial)
- **`src/excel_import/template_generator.py`** - Excel template generator

## Current State

### What Works:
- Basic Excel file reading
- Simple employee record creation
- Template file generation
- Basic UI for file selection

### What's Missing:
1. **Complete field mapping** - Not all employee fields are imported
2. **Contact information** - Phone and email not imported (see ISSUE-051)
3. **Relationship handling** - CACES, medical visits, trainings not imported
4. **Validation** - Insufficient validation before import
5. **Error handling** - Poor error reporting and rollback
6. **Progress tracking** - No progress indication for large imports
7. **Duplicate detection** - No duplicate matricule detection
8. **Batch processing** - No transaction batching for performance

## Expected Behavior

### 1. Complete Field Mapping

Import should support ALL employee fields:
- ✅ first_name
- ✅ last_name
- ✅ matricule
- ✅ position
- ✅ department
- ✅ status
- ✅ entry_date
- ❌ phone_number (missing - see ISSUE-051)
- ❌ email_address (missing - see ISSUE-051)
- ❌ CACES certifications (not implemented)
- ❌ Medical visits (not implemented)
- ❌ Trainings (not implemented)

### 2. Multi-Sheet Import

Excel file should have multiple sheets:
- **Sheet 1: Employees** - Basic employee information
- **Sheet 2: CACES** - Certification records
- **Sheet 3: Medical** - Medical visit records
- **Sheet 4: Training** - Training records

### 3. Validation

Pre-import validation should check:
- Required fields present
- Matricule uniqueness
- Valid email format
- Valid phone format
- Valid dates
- Valid status values
- Foreign key integrity (position, department)

### 4. Error Handling

- Collect all validation errors before import
- Show detailed error report
- Allow user to fix and retry
- Rollback on import failure
- Log all errors

### 5. Progress Tracking

For large datasets (50-100 employees):
- Show progress bar
- Display "Processing X of Y records"
- Show elapsed/estimated time
- Allow cancellation

### 6. Duplicate Detection

- Check for duplicate matricules
- Warn user of duplicates
- Allow: skip, update, or cancel

### 7. Transaction Management

- Use database transactions
- Batch inserts (10-20 records per transaction)
- Commit on success, rollback on failure
- Maintain data integrity

## Proposed Solution

### Phase 1: Complete Employee Import (2-3 days)

**1.1 Add Missing Field Support**
- Import phone_number (when ISSUE-051 is fixed)
- Import email_address (when ISSUE-051 is fixed)
- Map all fields correctly

**1.2 Improve Validation**
```python
def validate_employee_row(row: dict) -> list[str]:
    """Validate employee row, return list of errors."""
    errors = []

    # Required fields
    if not row.get('first_name'):
        errors.append("First name is required")
    if not row.get('last_name'):
        errors.append("Last name is required")
    if not row.get('matricule'):
        errors.append("Matricule is required")

    # Unique matricule
    if Employee.select().where(Employee.matricule == row['matricule']).exists():
        errors.append(f"Matricule {row['matricule']} already exists")

    # Valid email format
    if row.get('email_address') and not validate_email(row['email_address']):
        errors.append(f"Invalid email format: {row['email_address']}")

    # Valid phone format
    if row.get('phone_number') and not validate_phone(row['phone_number']):
        errors.append(f"Invalid phone format: {row['phone_number']}")

    # Valid date
    try:
        parse_date(row['entry_date'])
    except:
        errors.append(f"Invalid entry date: {row['entry_date']}")

    return errors
```

**1.3 Batch Processing**
```python
def import_employees_in_batches(employees: list[dict], batch_size=20):
    """Import employees in batches for performance."""
    total = len(employees)
    imported = 0
    errors = []

    with database.atomic():
        for i in range(0, total, batch_size):
            batch = employees[i:i + batch_size]

            for employee_data in batch:
                try:
                    Employee.create(**employee_data)
                    imported += 1
                    update_progress(imported, total)
                except Exception as e:
                    errors.append({
                        'employee': employee_data,
                        'error': str(e)
                    })

    return imported, errors
```

### Phase 2: Multi-Sheet Import (2-3 days)

**2.1 CACES Import**
- Read CACES sheet
- Validate employee references
- Import CACES records
- Handle related employees

**2.2 Medical Visits Import**
- Read Medical sheet
- Validate employee references
- Import medical visit records
- Calculate next due dates

**2.3 Training Import**
- Read Training sheet
- Validate employee references
- Import training records
- Handle expiring certifications

### Phase 3: Improve UI (2 days)

**File: `src/ui_ctk/views/import_view.py`**

Add:
- File preview with row count
- Validation results display
- Progress bar for import
- Error report with details
- Success/failure summary
- Retry capability

### Phase 4: Template Generator (1 day)

**File: `src/excel_import/template_generator.py`**

Create comprehensive template with:
- All employee fields
- Example data
- Data validation rules
- Instructions sheet
- Dropdown lists for position, department, status

## Dependencies

- ISSUE-051: Missing Contact Fields (phone, email)
- ISSUE-047: Missing Data Entry Forms (for manual fix capability)
- Validation utilities: ✅ Complete

## Related Issues

- ISSUE-051: Missing Contact Information Fields
- ISSUE-047: Missing Data Entry Forms
- ISSUE-053: Incomplete Excel Export

## Acceptance Criteria

- [ ] All employee fields import correctly
- [ ] Phone and email import (when ISSUE-051 fixed)
- [ ] CACES records import from separate sheet
- [ ] Medical visits import from separate sheet
- [ ] Training records import from separate sheet
- [ ] Validation catches all errors before import
- [ ] Duplicate matricules detected
- [ ] Progress bar shows import progress
- [ ] Transactions ensure data integrity
- [ ] Rollback works on failure
- [ ] Error report is detailed and helpful
- [ ] Template file includes all fields and examples
- [ ] Can import 50-100 employees in < 30 seconds
- [ ] All tests pass

## Estimated Effort

**Total:** 5-7 days
- Complete employee import: 2-3 days
- Multi-sheet import: 2-3 days
- Improve UI: 2 days
- Template generator: 1 day

## Notes

This is a critical feature for production deployment. Manual data entry for 50+ employees is not practical. The import feature must be robust, validated, and handle errors gracefully.

## Use Cases

1. **Initial System Setup** - Import 50-100 existing employees
2. **Bulk Updates** - Import updated data from HR system
3. **Migration from Legacy System** - Migrate all employee data
4. **Regular Updates** - Weekly/monthly bulk updates

## Performance Targets

- 50 employees: < 10 seconds
- 100 employees: < 20 seconds
- 500 employees: < 60 seconds
- 1000 employees: < 120 seconds

## References

- openpyxl documentation: https://openpyxl.readthedocs.io/
- Excel file format best practices: https://www.ibm.com/docs/en/ssd_for_is?topic=formats-excel-file-format
