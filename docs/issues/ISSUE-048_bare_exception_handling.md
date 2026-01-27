# ISSUE-048: Bare Exception Handlers

## Description

Multiple files contain bare `except:` statements and overly broad exception handlers that catch all exceptions without proper handling. This makes debugging extremely difficult and can mask serious errors.

## Affected Files

### Bare `except:` statements:

1. `src/export/data_exporter.py:207`
2. `src/export/data_exporter.py:252`
3. `src/export/data_exporter.py:297`
4. `src/export/data_exporter.py:342`
5. `src/ui_ctk/forms/employee_form.py:435`
6. `src/ui_ctk/views/employee_detail.py:582`
7. `src/ui_ctk/views/employee_detail.py:591`
8. `src/ui_ctk/views/employee_list.py:326`

### Broad `except Exception:` statements:

1. `src/utils/undo_manager.py:124`
2. `src/utils/undo_manager.py:139`
3. `src/utils/undo_manager.py:193`
4. `src/utils/undo_manager.py:210`
5. `src/utils/undo_manager.py:274`
6. `src/utils/undo_manager.py:296`
7. `src/utils/undo_manager.py:485`
8. `src/state/app_state.py:79`
9. `src/lock/manager.py:170`
10. `src/lock/manager.py:318`
11. `src/excel_import/excel_importer.py:476`

## Current State

```python
# Example from src/export/data_exporter.py:207
try:
    # ... some code ...
except:
    pass  # Masks ALL errors!
```

```python
# Example from src/utils/undo_manager.py:124
try:
    # ... some code ...
except Exception as e:
    log_error(e)  # Too broad, catches system errors
```

## Problems

1. **Debugging Impossible:** Bare `except:` catches everything including `KeyboardInterrupt` and `SystemExit`, making it impossible to terminate the program during debugging
2. **Masks Serious Errors:** Database errors, file I/O errors, and memory errors are silently swallowed
3. **No Error Context:** Errors are caught without logging what went wrong
4. **Data Corruption Risk:** Database operations can fail silently, leading to data corruption
5. **Security Risk:** Security-related exceptions are caught and ignored

## Expected Behavior

All exception handlers should:
1. Catch specific exception types only
2. Log the error with context
3. Either handle the error properly or re-raise
4. Never catch `SystemExit`, `KeyboardInterrupt`, or `GeneratorExit`

## Proposed Solution

### Phase 1: Replace Bare `except:` (Critical)

Replace all bare `except:` statements with specific exceptions:

**Before:**
```python
try:
    save_employee(data)
except:
    return False
```

**After:**
```python
try:
    save_employee(data)
except (ValueError, DatabaseError) as e:
    logger.error(f"Failed to save employee: {e}")
    return False
except Exception as e:
    logger.critical(f"Unexpected error saving employee: {e}")
    raise  # Re-raise unexpected errors
```

### Phase 2: Narrow Broad Exception Handlers

Replace broad `except Exception:` with specific types:

**Before:**
```python
try:
    export_to_excel(data)
except Exception as e:
    log_error(e)
```

**After:**
```python
try:
    export_to_excel(data)
except PermissionError as e:
    logger.error(f"Permission denied writing Excel file: {e}")
    show_error("Cannot write to file - check permissions")
except FileNotFoundError as e:
    logger.error(f"Directory not found: {e}")
    show_error("Output directory does not exist")
except openpyxl.utils.exceptions.InvalidFileException as e:
    logger.error(f"Invalid Excel file format: {e}")
    show_error("Invalid Excel file format")
except Exception as e:
    logger.critical(f"Unexpected error during export: {e}")
    show_error("Unexpected error occurred")
    raise
```

### Phase 3: Add Proper Error Logging

1. Ensure all exception handlers log the error
2. Include context (what operation was being performed)
3. Log stack trace for unexpected errors
4. Use appropriate log levels (error, critical, warning)

## Common Exception Patterns

### Database Operations
```python
except peewee.IntegrityError as e:
    logger.error(f"Database integrity error: {e}")
    show_error("Data conflict - record may already exist")
except peewee.DatabaseError as e:
    logger.error(f"Database error: {e}")
    show_error("Database operation failed")
```

### File Operations
```python
except PermissionError as e:
    logger.error(f"Permission denied: {e}")
    show_error("No permission to access file")
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    show_error("File not found")
except IsADirectoryError as e:
    logger.error(f"Expected file, got directory: {e}")
    show_error("Invalid file path")
```

### Validation
```python
except ValueError as e:
    logger.warning(f"Invalid value: {e}")
    show_error(f"Invalid input: {e}")
except KeyError as e:
    logger.error(f"Missing required key: {e}")
    show_error("Required data missing")
```

## Implementation Strategy

1. **Start with Critical Files:** Begin with `data_exporter.py` and undo operations
2. **Add Unit Tests:** Test error conditions for each fixed handler
3. **Code Review:** Review all changes to ensure proper error handling
4. **Integration Testing:** Test that errors are properly propagated

## Dependencies

- Logging infrastructure: ✅ Complete (`src/utils/logging_config.py`)
- Error handler utilities: ✅ Complete (`src/utils/error_handler.py`)

## Related Issues

- ISSUE-010: Broad Exception Handling (historical issue)

## Acceptance Criteria

- [ ] No bare `except:` statements remain in the codebase
- [ ] All exception handlers catch specific exception types
- [ ] All exception handlers log errors with context
- [ ] Unexpected errors are re-raised after logging
- [ ] SystemExit, KeyboardInterrupt, GeneratorExit are never caught
- [ ] Unit tests exist for error conditions
- [ ] Code review approved

## Estimated Effort

**Total:** 3-4 days
- Replace bare `except:` statements: 1 day
- Narrow broad exception handlers: 1-2 days
- Add comprehensive logging: 1 day
- Write unit tests: 1 day

## Notes

This is a critical code quality issue that affects the reliability and maintainability of the entire application. Proper error handling is essential for production use.

## References

- Python Exception Handling Best Practices: https://docs.python.org/3/tutorial/errors.html
- Never use bare `except:`: https://flake8.pycqa.org/en/3.9.0/user/error-codes.html#E722
