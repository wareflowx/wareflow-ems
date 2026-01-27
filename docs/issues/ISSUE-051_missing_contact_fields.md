# ISSUE-051: Missing Contact Information Fields

## Description

The Employee model is missing critical contact information fields: phone number and email address. These are essential for operational communication and initial data import from existing systems.

## Affected Files

- **`src/employee/models.py`** - Employee model definition
- **`src/ui_ctk/forms/employee_form.py`** - Employee form
- **`src/export/data_exporter.py`** - Excel export
- **`src/excel_import/excel_importer.py`** - Excel import
- Database migrations

## Current State

Employee model has these fields:
- first_name
- last_name
- matricule
- position
- department
- status
- entry_date

**Missing:**
- phone_number ❌
- email_address ❌

## Expected Behavior

Employee model should include:

### 1. Phone Number Field
```python
phone_number = CharField(
    max_length=20,
    null=True,
    index=False,
    help_text="Contact phone number"
)
```

**Requirements:**
- Optional field (nullable)
- Support international formats (+33, +1, etc.)
- Min 10 characters, max 20 characters
- Validate phone number format
- Support spaces, dashes, parentheses

### 2. Email Address Field
```python
email_address = CharField(
    max_length=255,
    null=True,
    index=True,
    help_text="Contact email address"
)
```

**Requirements:**
- Optional field (nullable)
- Validate email format
- Unique (optional - may not need uniqueness constraint)
- Max 255 characters (standard email length)

## Impact

- **HIGH:** Cannot collect employee contact information
- **HIGH:** Cannot import data from systems with contact info
- **MEDIUM:** Incomplete employee records
- **MEDIUM:** Cannot contact employees for certifications/expiring items

## Proposed Solution

### Phase 1: Database Migration (1 day)

1. **Create Migration Script**
   - Add `phone_number` column to employees table
   - Add `email_address` column to employees table
   - Make both nullable (don't break existing data)
   - Add index on email_address for lookups

2. **Migration File: `src/database/migrations/00X_add_contact_fields.py`**
   ```python
   def upgrade():
       migrate(
           migrator.add_column('employees', 'phone_number',
                             CharField(max_length=20, null=True)),
           migrator.add_column('employees', 'email_address',
                             CharField(max_length=255, null=True, index=True)),
       )

   def downgrade():
       migrate(
           migrator.remove_column('employees', 'phone_number'),
           migrator.remove_column('employees', 'email_address'),
       )
   ```

3. **Test Migration**
   - Run migration on test database
   - Verify existing records not affected
   - Test rollback

### Phase 2: Update Model (1 day)

**File: `src/employee/models.py`**

Add to Employee model:
```python
class Employee(BaseModel):
    # ... existing fields ...

    phone_number = CharField(
        max_length=20,
        null=True,
        column_name='phone_number',
        help_text="Contact phone number (international format supported)"
    )

    email_address = CharField(
        max_length=255,
        null=True,
        index=True,
        column_name='email_address',
        help_text="Contact email address"
    )

    # ... rest of model ...
```

Add property for formatted phone number:
```python
@property
def formatted_phone(self):
    """Return phone number in formatted display."""
    if not self.phone_number:
        return "N/A"
    # Add formatting logic if needed
    return self.phone_number
```

### Phase 3: Update Import/Export (1 day)

**File: `src/export/data_exporter.py`**
- Add phone_number to Excel export columns
- Add email_address to Excel export columns

**File: `src/excel_import/excel_importer.py`**
- Map phone_number column during import
- Map email_address column during import
- Add validation for both fields

### Phase 4: Update UI Forms (1 day)

**File: `src/ui_ctk/forms/employee_form.py`**
- Add phone number input field (optional)
- Add email address input field (optional)
- Add validation for phone format
- Add validation for email format
- Update field layout

### Phase 5: Update Views (1 day)

**Files:**
- `src/ui_ctk/views/employee_list.py` - Add columns to table
- `src/ui_ctk/views/employee_detail.py` - Display in details view

## Validation Rules

### Phone Number Validation

```python
def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    if not phone:
        return True  # Optional field

    # Remove spaces, dashes, parentheses
    digits_only = re.sub(r'[^\d+]', '', phone)

    # Check length: 10-15 digits with optional +
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False

    # Must start with + or digit
    if not (digits_only.startswith('+') or digits_only[0].isdigit()):
        return False

    return True
```

### Email Address Validation

Use `email-validator` library for proper validation:

```python
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return True  # Optional field

    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False
```

## Dependencies

- **New dependency required:** `email-validator>=2.0.0`
- Add to `pyproject.toml`

## Related Issues

- ISSUE-047: Missing Data Entry Forms
- ISSUE-052: Incomplete Bulk Import Functionality
- ISSUE-053: Incomplete Excel Export

## Acceptance Criteria

- [ ] Migration script created and tested
- [ ] Model updated with both fields
- [ ] Phone number validation implemented
- [ ] Email address validation implemented
- [ ] Export includes both fields
- [ ] Import supports both fields
- [ ] UI form includes both fields
- [ ] Employee list view shows both fields
- [ ] Employee detail view shows both fields
- [ ] All tests pass
- [ ] Migration tested on production-like database

## Estimated Effort

**Total:** 3-4 days
- Migration: 1 day
- Model update: 1 day
- Import/Export: 1 day
- UI forms: 1 day

## Notes

Both fields should be optional (nullable) to avoid breaking existing employee records. This is a critical field for production use as most organizations need to contact employees regarding certifications and training.

## References

- Email validation library: https://pypi.org/project/email-validator/
- E.164 phone format: https://www.twilio.com/docs/glossary/what-e164
