# ISSUE-047: Missing Data Entry Forms

## Description

Core data entry forms are incomplete or missing, preventing users from creating and editing employee data, certifications, medical visits, and training records through the desktop UI.

## Affected Files

- `src/ui_ctk/forms/employee_form.py` - Employee creation/editing
- `src/ui_ctk/forms/caces_form.py` - CACES certification form
- `src/ui_ctk/forms/medical_form.py` - Medical visit form
- `src/ui_ctk/forms/training_form.py` - Training form (may not exist)

## Current State

Forms directory exists but implementations are basic or incomplete:
- Employee form exists but lacks proper validation and field completeness
- CACES form exists but needs enhancement
- Medical form exists but needs enhancement
- Training form may be missing entirely

## Expected Behavior

### 1. Employee Form (`src/ui_ctk/forms/employee_form.py`)

**Required Fields:**
- First Name (required, text)
- Last Name (required, text)
- Matricule (required, unique, text)
- Position (required, dropdown from predefined list)
- Department (required, dropdown from predefined list)
- Status (required, dropdown: Active/Inactive)
- Entry Date (required, date picker)
- **Phone Number (optional, text)** ⚠️ MISSING
- **Email Address (optional, text)** ⚠️ MISSING

**Form Features:**
- Real-time validation
- Unique matricule validation
- Field-level error messages
- Cancel and Save buttons
- Confirmation dialog on save
- Support for both create and edit modes

### 2. CACES Form (`src/ui_ctk/forms/caces_form.py`)

**Required Fields:**
- Employee (required, dropdown/autocomplete)
- CACES Type (required, dropdown from predefined list)
- Certificate Number (required, text)
- Issue Date (required, date picker)
- Expiration Date (required, date picker, must be > issue date)
- Document Upload (optional, file picker for PDF)

**Form Features:**
- Employee autocomplete search
- Expiration date validation
- Warning if expiration date < 90 days away
- Document preview if uploaded
- Document validation (PDF only, max 5MB)
- Cancel and Save buttons
- Edit mode support

### 3. Medical Visit Form (`src/ui_ctk/forms/medical_form.py`)

**Required Fields:**
- Employee (required, dropdown/autocomplete)
- Visit Date (required, date picker)
- Visit Type (required, dropdown: Initial/Periodic/Capacity)
- Next Due Date (required, date picker, must be > visit date)
- Doctor Name (optional, text)
- Notes (optional, text area)
- Document Upload (optional, file picker for PDF)

**Form Features:**
- Employee autocomplete search
- Next due date validation
- Warning if next due date < 90 days away
- Document preview if uploaded
- Document validation (PDF only, max 5MB)
- Cancel and Save buttons
- Edit mode support

### 4. Training Form (`src/ui_ctk/forms/training_form.py`)

**Required Fields:**
- Employee (required, dropdown/autocomplete)
- Training Name (required, text)
- Training Date (required, date picker)
- Certificate Number (optional, text)
- Expiration Date (optional, date picker)
- Trainer/Provider (optional, text)
- Notes (optional, text area)
- Document Upload (optional, file picker for PDF)

**Form Features:**
- Employee autocomplete search
- Expiration date validation (if provided)
- Warning if expiration date < 90 days away
- Document preview if uploaded
- Document validation (PDF only, max 5MB)
- Cancel and Save buttons
- Edit mode support

## Impact

- **HIGH:** Users cannot create employee records through UI
- Manual database manipulation required
- Cannot update certification information
- Cannot record medical visits
- Cannot track training records
- Desktop application is incomplete

## Root Cause

Forms were partially implemented but not completed. Focus was on backend logic rather than UI forms.

## Proposed Solution

### Phase 1: Enhance Employee Form (2 days)
1. Add missing phone and email fields (see ISSUE-051)
2. Implement real-time validation
3. Add unique matricule check
4. Improve field layout and grouping
5. Add form mode handling (create vs edit)
6. Add confirmation dialogs
7. Test with various input scenarios

### Phase 2: Enhance CACES Form (1-2 days)
1. Add employee autocomplete search
2. Implement date validation logic
3. Add expiration warnings
4. Add document upload functionality
5. Add document preview
6. Implement file validation (PDF, max 5MB)
7. Add edit mode support

### Phase 3: Enhance Medical Form (1-2 days)
1. Add employee autocomplete search
2. Implement date validation logic
3. Add next due date warnings
4. Add document upload functionality
5. Add document preview
6. Implement file validation (PDF, max 5MB)
7. Add edit mode support

### Phase 4: Create Training Form (2 days)
1. Create new training form class
2. Implement all required fields
3. Add employee autocomplete search
4. Implement validation logic
5. Add document upload functionality
6. Test all form scenarios

## Dependencies

- ISSUE-051: Add phone and email fields to Employee model
- File validation utilities: ✅ Complete
- Document storage: 🟡 Needs implementation

## Related Issues

- ISSUE-046: Missing UI Views
- ISSUE-051: Missing Contact Information Fields
- ISSUE-062: Document Upload and Preview

## Acceptance Criteria

- [ ] Employee form includes all required fields plus phone and email
- [ ] All forms have real-time validation
- [ ] All forms show field-level error messages
- [ ] Employee autocomplete works in all forms
- [ ] Date validation prevents invalid dates
- [ ] Expiration warnings show for dates < 90 days away
- [ ] Document upload accepts PDF only, max 5MB
- [ ] Document preview works for uploaded files
- [ ] All forms support both create and edit modes
- [ ] Forms integrate properly with views

## Estimated Effort

**Total:** 6-8 days
- Employee Form: 2 days
- CACES Form: 1-2 days
- Medical Form: 1-2 days
- Training Form: 2 days

## Notes

The business logic for saving and retrieving data is 100% complete. Forms need to integrate with existing controller methods. Focus on UX, validation, and error handling.
