# ISSUE-066: Make Employee Creation Fields Optional

## Description

Currently, when creating a new employee, too many fields are mandatory. Users want to be able to create an employee quickly with minimal information and complete the rest later. Only essential fields should be required: first name, last name, workspace, and role.

## Current State

**Employee form requires 7 fields:**
- First name (required)
- Last name (required)
- Status (required - defaults to "Active")
- Workspace (required)
- Role (required)
- Contract type (required)
- Entry date (required)

**Email and phone are already optional.**

## Problem

When creating a new employee, users must fill in all fields including contract type and entry date, which may not be immediately available. This slows down employee onboarding and creates friction in the workflow.

## Expected Behavior

### Minimum Required Fields

Only these 4 fields should be mandatory:
- **First name** - required
- **Last name** - required
- **Workspace** - required (e.g., Quai, Zone A, Zone B, Bureau)
- **Role** - required (e.g., Cariste, Préparateur, Magasinier)

### Optional Fields with Defaults

These fields should be optional:
- **Status** - optional, defaults to "Actif" if not provided
- **Contract type** - optional, can be null/empty
- **Entry date** - optional, can be null/empty
- **Email** - optional (already implemented)
- **Phone** - optional (already implemented)

## Affected Files

- `src/ui_ctk/forms/employee_form.py` - Remove required indicators, update validation
- `src/employee/validators.py` - Allow null values for optional fields
- `src/controllers/employee_controller.py` - Handle optional fields in create/update

## Implementation Plan

1. Update form UI to remove `*` from optional field labels
2. Update `validate()` method to only check required fields
3. Update `save()` method to handle None values for optional fields
4. Update validator/controller to accept null values
5. Test employee creation with minimum fields
6. Test employee creation with all fields
7. Test employee edit mode to ensure optional fields remain optional

## Acceptance Criteria

- [ ] Can create employee with only: first name, last name, workspace, role
- [ ] Status defaults to "Actif" when not specified
- [ ] Contract type can be left empty
- [ ] Entry date can be left empty
- [ ] Form validation only checks required fields
- [ ] No errors when saving employee without optional fields
- [ ] Edit mode works the same way (optional fields are optional)
- [ ] All tests pass

## Estimated Effort

**Total:** 2-3 hours
- Form UI updates: 30 minutes
- Validation logic updates: 30 minutes
- Controller/validator updates: 30 minutes
- Testing: 1 hour

## Related Issues

None

## Example Use Cases

### Use Case 1: Quick Employee Creation

1. New temp worker arrives
2. HR opens "Add Employee" form
3. Enters: First name "Jean", Last name "Dupont", Workspace "Zone A", Role "Préparateur"
4. Leaves: Contract type and Entry date empty
5. Clicks "Save"
6. Employee created successfully with defaults applied

### Use Case 2: Complete Employee Creation

1. New permanent hire
2. HR opens "Add Employee" form
3. Enters all fields including contract type "CDI" and entry date "01/03/2026"
4. Clicks "Save"
5. Employee created with all information

### Use Case 3: Progressive Data Entry

1. Create employee with minimal info
2. Employee appears in list
3. Later, edit employee to add contract type and entry date
4. Information is progressively completed

## Notes

This improvement makes the employee creation process more flexible and user-friendly. It aligns with real-world HR workflows where not all information is available at the time of initial employee record creation.
