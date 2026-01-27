# ISSUE-053: Incomplete Excel Export Functionality

## Description

The Excel export feature exists but is incomplete (approximately 60% done). Users need to export data for reporting and analysis, but the current implementation lacks formatting, multiple sheets support, and comprehensive data export.

## Affected Files

- **`src/export/data_exporter.py`** - Main export logic (partial)
- **`src/controllers/export_controller.py`** - Export controller
- **`src/ui_ctk/widgets/export_button.py`** - Export button widget
- **`src/ui_ctk/dialogs/export_dialog.py`** - Export dialog

## Current State

### What Works:
- Basic Excel file creation
- Employee data export
- Export dialog UI
- Progress tracking
- File selection

### What's Missing:
1. **Formatting** - No cell formatting (colors, fonts, borders)
2. **Multiple Sheets** - Only exports basic employee data
3. **Contact Information** - Phone and email not exported (see ISSUE-051)
4. **Headers** - No freeze panes, no bold headers
5. **Filters** - No auto-filter on header row
6. **Related Data** - CACES, medical visits, trainings not exported
7. **Conditional Formatting** - No color coding for expiration warnings
8. **Column Widths** - Auto-width not set
9. **Data Validation** - No data type validation
10. **Summary Statistics** - No summary sheets

## Expected Behavior

### 1. Multi-Sheet Export

Excel file should contain multiple sheets:

**Sheet 1: Employees**
- All employee fields
- Formatting: headers bold, frozen top row, auto-filter
- Column widths adjusted
- Contact information (when ISSUE-051 fixed)

**Sheet 2: CACES**
- All CACES certifications
- Employee name (linked via matricule)
- Expiration date
- Color coding: Red (< 30 days), Orange (30-60 days), Yellow (60-90 days)
- Count summary at top

**Sheet 3: Medical Visits**
- All medical visit records
- Employee name (linked via matricule)
- Visit date and next due date
- Color coding for expiring visits
- Count summary at top

**Sheet 4: Training**
- All training records
- Employee name (linked via matricule)
- Training date and expiration
- Color coding for expiring training
- Count summary at top

**Sheet 5: Summary**
- Employee counts by status
- Employee counts by department
- Employee counts by position
- Expiring certifications counts
- Alerts summary

### 2. Formatting

**Headers:**
- Bold font
- Gray background
- White text
- Freeze top row
- Auto-filter enabled

**Data:**
- Alternating row colors (zebra striping)
- Text wrap where appropriate
- Date formatting: DD/MM/YYYY
- Number formatting where appropriate
- Alignment: left for text, right for numbers, center for status

**Conditional Formatting:**
- Red background: Expiration < 30 days
- Orange background: Expiration 30-60 days
- Yellow background: Expiration 60-90 days
- Green background: No expiration or > 90 days

**Column Widths:**
- Auto-fit to content
- Minimum width: 10 characters
- Maximum width: 50 characters

### 3. Data Export Options

User should be able to select:
- ✅ Include CACES (checkbox)
- ✅ Include Medical Visits (checkbox)
- ✅ Include Training (checkbox)
- ✅ Include Summary (checkbox)
- ❌ Date range filter (missing)
- ❌ Status filter (missing)
- ❌ Department filter (missing)

## Proposed Solution

### Phase 1: Enhance Employee Export (2 days)

**1.1 Add Formatting**
```python
def format_headers(sheet):
    """Apply formatting to header row."""
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
```

**1.2 Add Conditional Formatting**
```python
def add_expiration_warning(sheet, column_index):
    """Add color coding for expiration dates."""
    red_rule = ColorScaleRule(
        start_type='num', start_value=0, start_color='63BE7B',
        mid_type='num', mid_value=30, mid_color='FFEB84',
        end_type='num', end_value=90, end_color='F8696B'
    )
    sheet.conditional_formatting.add(f"{get_column_letter(column_index)}2:{get_column_letter(column_index)}{sheet.max_row}", red_rule)
```

**1.3 Auto-Width Columns**
```python
def auto_width_columns(sheet):
    """Auto-adjust column widths."""
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass

        adjusted_width = min(max(max_length + 2, 10), 50)
        sheet.column_dimensions[column_letter].width = adjusted_width
```

### Phase 2: Add Related Data Sheets (2-3 days)

**2.1 CACES Sheet**
```python
def create_caces_sheet(workbook, employees):
    """Create CACES certifications sheet."""
    sheet = workbook.create_sheet("CACES", 1)

    # Add headers
    headers = ["Matricule", "Name", "CACES Type", "Certificate #",
               "Issue Date", "Expiration Date", "Status"]
    sheet.append(headers)

    # Add data
    for employee in employees:
        for caces in employee.caces:
            status = get_expiration_status(caces.expiration_date)
            sheet.append([
                employee.matricule,
                employee.full_name,
                caces.caces_type,
                caces.certificate_number,
                caces.issue_date,
                caces.expiration_date,
                status
            ])

    apply_conditional_formatting(sheet, expiration_column=6)
    format_headers(sheet)
    auto_width_columns(sheet)
```

**2.2 Medical Visits Sheet**
- Similar to CACES sheet
- Include visit date, next due date
- Color code by next due date

**2.3 Training Sheet**
- Similar to CACES sheet
- Include training date, expiration
- Color code by expiration

### Phase 3: Add Summary Sheet (1 day)

```python
def create_summary_sheet(workbook):
    """Create summary statistics sheet."""
    sheet = workbook.create_sheet("Summary", 0)

    # Employee Counts
    sheet.append("Employee Counts")
    sheet.append(["Status", "Count"])
    sheet.append(["Active", Employee.select().where(Employee.status == "active").count()])
    sheet.append(["Inactive", Employee.select().where(Employee.status == "inactive").count()])
    sheet.append([])

    # Department Counts
    sheet.append("Employees by Department")
    sheet.append(["Department", "Count"])
    for dept in Employee.select(Employee.department).distinct():
        count = Employee.select().where(Employee.department == dept.department).count()
        sheet.append([dept.department, count])

    apply_formatting(sheet)
```

### Phase 4: Add Export Options (1 day)

**File: `src/ui_ctk/dialogs/export_dialog.py`**

Add filters:
- Date range picker
- Status filter (Active/Inactive/All)
- Department filter
- Position filter

## Dependencies

- ISSUE-051: Missing Contact Fields (phone, email)
- Employee queries: ✅ Complete
- Alert calculations: ✅ Complete

## Related Issues

- ISSUE-051: Missing Contact Information Fields
- ISSUE-052: Incomplete Bulk Import
- ISSUE-062: Document Upload and Preview

## Acceptance Criteria

- [ ] Employee sheet has formatted headers
- [ ] All sheets have frozen top row
- [ ] All sheets have auto-filter
- [ ] Column widths auto-adjust
- [ ] Conditional formatting for expiration dates
- [ ] CACES sheet exports with color coding
- [ ] Medical visits sheet exports with color coding
- [ ] Training sheet exports with color coding
- [ ] Summary sheet exports with statistics
- [ ] Phone and email included (when ISSUE-051 fixed)
- [ ] Export dialog has filter options
- [ ] Export 100 employees in < 10 seconds
- [ ] Export 500 employees in < 30 seconds
- [ ] File opens correctly in Excel
- [ ] All tests pass

## Estimated Effort

**Total:** 5-6 days
- Enhance employee export: 2 days
- Add related data sheets: 2-3 days
- Add summary sheet: 1 day
- Add export options: 1 day

## Notes

The export feature is critical for reporting and data analysis. Excel is the intended "read" interface for this application, so the export must be comprehensive and well-formatted.

## Performance Targets

- 50 employees: < 5 seconds
- 100 employees: < 10 seconds
- 500 employees: < 30 seconds
- 1000 employees: < 60 seconds

## References

- openpyxl formatting: https://openpyxl.readthedocs.io/en/stable/formatting.html
- Excel conditional formatting: https://openpyxl.readthedocs.io/en/stable/formatting.html#conditional-formatting
